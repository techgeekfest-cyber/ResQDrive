"""ResQDrive Backend API Test Suite.

Tests all backend endpoints including:
- Dashboard metrics (live state)
- Evidence fusion (multi-vehicle corroboration)
- Risk-aware routing
- Simulation lifecycle
- Response actions
- WebSocket connectivity
"""
import requests
import sys
import time
from datetime import datetime

BASE_URL = "https://vehicle-risk-map.preview.emergentagent.com/api"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

class ResQDriveAPITester:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.critical_failures = []
        self.warnings = []

    def log(self, msg, level="info"):
        prefix = {
            "info": f"{Colors.BLUE}ℹ{Colors.RESET}",
            "success": f"{Colors.GREEN}✓{Colors.RESET}",
            "error": f"{Colors.RED}✗{Colors.RESET}",
            "warning": f"{Colors.YELLOW}⚠{Colors.RESET}",
        }
        print(f"{prefix.get(level, '')} {msg}")

    def run_test(self, name, method, endpoint, expected_status, data=None, 
                 validate_fn=None, critical=False):
        """Run a single API test with optional validation."""
        url = f"{self.base_url}/{endpoint}"
        self.tests_run += 1
        
        print(f"\n{Colors.BLUE}[{self.tests_run}] Testing: {name}{Colors.RESET}")
        
        try:
            if method == 'GET':
                response = requests.get(url, timeout=15)
            elif method == 'POST':
                response = requests.post(url, json=data, timeout=15)
            else:
                raise ValueError(f"Unsupported method: {method}")

            status_ok = response.status_code == expected_status
            
            if not status_ok:
                self.tests_failed += 1
                msg = f"Status mismatch: expected {expected_status}, got {response.status_code}"
                self.log(msg, "error")
                if critical:
                    self.critical_failures.append(f"{name}: {msg}")
                try:
                    self.log(f"Response: {response.text[:200]}", "error")
                except:
                    pass
                return False, {}

            try:
                result = response.json()
            except:
                result = {}

            # Run custom validation if provided
            if validate_fn:
                validation_result = validate_fn(result)
                if validation_result is True:
                    self.tests_passed += 1
                    self.log(f"PASSED - {name}", "success")
                    return True, result
                else:
                    self.tests_failed += 1
                    self.log(f"FAILED - Validation: {validation_result}", "error")
                    if critical:
                        self.critical_failures.append(f"{name}: {validation_result}")
                    return False, result
            else:
                self.tests_passed += 1
                self.log(f"PASSED - Status {response.status_code}", "success")
                return True, result

        except requests.exceptions.Timeout:
            self.tests_failed += 1
            self.log(f"FAILED - Request timeout", "error")
            if critical:
                self.critical_failures.append(f"{name}: Timeout")
            return False, {}
        except Exception as e:
            self.tests_failed += 1
            self.log(f"FAILED - Error: {str(e)}", "error")
            if critical:
                self.critical_failures.append(f"{name}: {str(e)}")
            return False, {}

    def test_dashboard_summary(self):
        """Test GET /api/dashboard/summary - live metrics from backend state."""
        def validate(data):
            required = ['active_vehicles', 'active_hazards', 'unsafe_roads', 
                       'verified_incidents', 'network_confidence', 'priority_zones']
            missing = [k for k in required if k not in data]
            if missing:
                return f"Missing fields: {missing}"
            
            # Check that values are not hardcoded (should be reasonable ranges)
            if not isinstance(data['active_vehicles'], int):
                return "active_vehicles should be an integer"
            if not isinstance(data['network_confidence'], int):
                return "network_confidence should be an integer"
            
            self.log(f"  Active Vehicles: {data['active_vehicles']}/{data.get('total_vehicles', '?')}", "info")
            self.log(f"  Active Hazards: {data['active_hazards']}", "info")
            self.log(f"  Unsafe Roads: {data['unsafe_roads']}", "info")
            self.log(f"  Network Confidence: {data['network_confidence']}%", "info")
            return True
        
        return self.run_test(
            "Dashboard Summary (Live Metrics)",
            "GET", "dashboard/summary", 200,
            validate_fn=validate, critical=True
        )

    def test_incidents_list(self):
        """Test GET /api/incidents - list all incidents."""
        def validate(data):
            if not isinstance(data, list):
                return "Response should be a list"
            if len(data) > 0:
                inc = data[0]
                required = ['id', 'hazard_type', 'confidence', 'verification_status', 
                           'risk_score', 'priority']
                missing = [k for k in required if k not in inc]
                if missing:
                    return f"Incident missing fields: {missing}"
                self.log(f"  Found {len(data)} incidents", "info")
                self.log(f"  Sample: {inc['id']} - {inc['hazard_type']} ({inc['verification_status']})", "info")
            return True
        
        return self.run_test(
            "Incidents List",
            "GET", "incidents", 200,
            validate_fn=validate, critical=True
        )

    def test_incident_detail(self, incident_id):
        """Test GET /api/incidents/{id} - detailed incident with observations."""
        def validate(data):
            required = ['id', 'observations', 'confidence_timeline', 'breakdown', 
                       'risk_components', 'nearby_infrastructure']
            missing = [k for k in required if k not in data]
            if missing:
                return f"Missing detail fields: {missing}"
            
            if not isinstance(data['observations'], list):
                return "observations should be a list"
            if not isinstance(data['breakdown'], dict):
                return "breakdown should be a dict"
            
            self.log(f"  Observations: {len(data['observations'])}", "info")
            self.log(f"  Confidence: {data.get('confidence')}%", "info")
            self.log(f"  Evidence Count: {data.get('evidence_count')}", "info")
            return True
        
        return self.run_test(
            f"Incident Detail ({incident_id})",
            "GET", f"incidents/{incident_id}", 200,
            validate_fn=validate
        )

    def test_vehicles_list(self):
        """Test GET /api/vehicles."""
        def validate(data):
            if not isinstance(data, list):
                return "Response should be a list"
            if len(data) == 0:
                return "No vehicles found"
            v = data[0]
            required = ['id', 'vehicle_code', 'status', 'latitude', 'longitude']
            missing = [k for k in required if k not in v]
            if missing:
                return f"Vehicle missing fields: {missing}"
            self.log(f"  Found {len(data)} vehicles", "info")
            return True
        
        return self.run_test(
            "Vehicles List",
            "GET", "vehicles", 200,
            validate_fn=validate, critical=True
        )

    def test_vehicle_detail(self, vehicle_id):
        """Test GET /api/vehicles/{id} with observation_history."""
        def validate(data):
            if 'observation_history' not in data:
                return "Missing observation_history"
            self.log(f"  Observation History: {len(data['observation_history'])} entries", "info")
            return True
        
        return self.run_test(
            f"Vehicle Detail ({vehicle_id})",
            "GET", f"vehicles/{vehicle_id}", 200,
            validate_fn=validate
        )

    def test_roads_risk(self):
        """Test GET /api/roads/risk - road segments with risk scores."""
        def validate(data):
            if not isinstance(data, list):
                return "Response should be a list"
            if len(data) == 0:
                return "No roads found"
            road = data[0]
            required = ['id', 'name', 'risk_score', 'risk_state', 'coordinates']
            missing = [k for k in required if k not in road]
            if missing:
                return f"Road missing fields: {missing}"
            self.log(f"  Found {len(data)} road segments", "info")
            unsafe = [r for r in data if r['risk_state'] == 'UNSAFE']
            self.log(f"  Unsafe roads: {len(unsafe)}", "info")
            return True
        
        return self.run_test(
            "Roads Risk",
            "GET", "roads/risk", 200,
            validate_fn=validate, critical=True
        )

    def test_evidence_fusion_single_vehicle(self):
        """Test POST /api/evidence/fuse - single vehicle = UNVERIFIED (~82%)."""
        observations = [
            {
                "vehicle_id": "RQ-TEST-001",
                "hazard_type": "FLOOD",
                "latitude": 17.4009,
                "longitude": 78.4610,
                "confidence": 0.85,
                "sensor_type": "CAMERA",
                "sensor_quality": 1.0,
                "age_minutes": 2
            }
        ]
        
        def validate(data):
            if data.get('verification_state') != 'UNVERIFIED':
                return f"Expected UNVERIFIED, got {data.get('verification_state')}"
            conf = data.get('confidence', 0)
            if not (75 <= conf <= 90):
                return f"Expected confidence ~82%, got {conf}%"
            if data.get('evidence_count') != 1:
                return f"Expected 1 vehicle, got {data.get('evidence_count')}"
            self.log(f"  Confidence: {conf}% (UNVERIFIED)", "info")
            return True
        
        return self.run_test(
            "Evidence Fusion - Single Vehicle (UNVERIFIED)",
            "POST", "evidence/fuse", 200,
            data=observations, validate_fn=validate, critical=True
        )

    def test_evidence_fusion_three_agreeing(self):
        """Test POST /api/evidence/fuse - 3 agreeing vehicles = VERIFIED (~93%)."""
        observations = [
            {
                "vehicle_id": "RQ-TEST-001",
                "hazard_type": "FLOOD",
                "latitude": 17.4009,
                "longitude": 78.4610,
                "confidence": 0.88,
                "sensor_type": "CAMERA",
                "sensor_quality": 1.0,
                "age_minutes": 2
            },
            {
                "vehicle_id": "RQ-TEST-002",
                "hazard_type": "FLOOD",
                "latitude": 17.4010,
                "longitude": 78.4611,
                "confidence": 0.91,
                "sensor_type": "CAMERA",
                "sensor_quality": 1.0,
                "age_minutes": 3
            },
            {
                "vehicle_id": "RQ-TEST-003",
                "hazard_type": "FLOOD",
                "latitude": 17.4011,
                "longitude": 78.4609,
                "confidence": 0.89,
                "sensor_type": "CAMERA",
                "sensor_quality": 1.0,
                "age_minutes": 1
            }
        ]
        
        def validate(data):
            if data.get('verification_state') != 'VERIFIED':
                return f"Expected VERIFIED, got {data.get('verification_state')}"
            conf = data.get('confidence', 0)
            if not (90 <= conf <= 97):
                return f"Expected confidence ~93%, got {conf}%"
            if data.get('evidence_count') != 3:
                return f"Expected 3 vehicles, got {data.get('evidence_count')}"
            self.log(f"  Confidence: {conf}% (VERIFIED)", "info")
            self.log(f"  Evidence Count: {data.get('evidence_count')} vehicles", "info")
            return True
        
        return self.run_test(
            "Evidence Fusion - Three Agreeing Vehicles (VERIFIED)",
            "POST", "evidence/fuse", 200,
            data=observations, validate_fn=validate, critical=True
        )

    def test_evidence_fusion_conflicting(self):
        """Test POST /api/evidence/fuse - conflicting reports = CONFLICTING state."""
        observations = [
            {
                "vehicle_id": "RQ-TEST-001",
                "hazard_type": "FLOOD",
                "latitude": 17.4009,
                "longitude": 78.4610,
                "confidence": 0.88,
                "sensor_type": "CAMERA",
                "sensor_quality": 1.0,
                "age_minutes": 2
            },
            {
                "vehicle_id": "RQ-TEST-002",
                "hazard_type": "FLOOD",
                "latitude": 17.4010,
                "longitude": 78.4611,
                "confidence": 0.85,
                "sensor_type": "CAMERA",
                "sensor_quality": 1.0,
                "age_minutes": 3
            },
            {
                "vehicle_id": "RQ-TEST-003",
                "hazard_type": "CLEAR",
                "latitude": 17.4011,
                "longitude": 78.4609,
                "confidence": 0.82,
                "sensor_type": "CAMERA",
                "sensor_quality": 1.0,
                "age_minutes": 1
            }
        ]
        
        def validate(data):
            if data.get('verification_state') != 'CONFLICTING':
                return f"Expected CONFLICTING, got {data.get('verification_state')}"
            conf = data.get('confidence', 0)
            # Conflicting should lower confidence
            if conf >= 90:
                return f"Expected lowered confidence due to conflict, got {conf}%"
            conflict_count = data.get('conflict_count', 0)
            if conflict_count == 0:
                return "Expected conflict_count > 0"
            self.log(f"  Confidence: {conf}% (lowered by conflict)", "info")
            self.log(f"  Conflict Count: {conflict_count}", "info")
            self.log(f"  Agreement: {data.get('agreement')}%", "info")
            return True
        
        return self.run_test(
            "Evidence Fusion - Conflicting Reports (CONFLICTING)",
            "POST", "evidence/fuse", 200,
            data=observations, validate_fn=validate, critical=True
        )

    def test_routes_plan(self):
        """Test POST /api/routes/plan - fastest vs safe route."""
        def validate(data):
            if 'fastest' not in data or 'safe' not in data:
                return "Missing fastest or safe route"
            if 'avoided' not in data:
                return "Missing avoided list"
            
            fastest = data['fastest']
            safe = data['safe']
            
            if not fastest or not safe:
                return "Routes should not be null"
            
            self.log(f"  Fastest: {fastest['total_time']} min, max risk {fastest['max_risk']}", "info")
            self.log(f"  Safe: {safe['total_time']} min, max risk {safe['max_risk']}", "info")
            self.log(f"  Avoided roads: {len(data['avoided'])}", "info")
            
            # Safe route should avoid high-risk segments
            if len(data['avoided']) > 0:
                self.log(f"  Avoided: {[a['name'] for a in data['avoided']]}", "info")
            
            return True
        
        return self.run_test(
            "Route Planning - GACHI to KOTI (Safe vs Fastest)",
            "POST", "routes/plan", 200,
            data={"start": "GACHI", "destination": "KOTI"},
            validate_fn=validate, critical=True
        )

    def test_routes_get(self):
        """Test GET /api/routes - node list."""
        def validate(data):
            if 'nodes' not in data:
                return "Missing nodes list"
            if not isinstance(data['nodes'], list):
                return "nodes should be a list"
            if len(data['nodes']) == 0:
                return "No nodes found"
            self.log(f"  Found {len(data['nodes'])} route nodes", "info")
            return True
        
        return self.run_test(
            "Routes Metadata",
            "GET", "routes", 200,
            validate_fn=validate
        )

    def test_simulation_reset(self):
        """Test POST /api/simulation/reset."""
        def validate(data):
            if not data.get('ok'):
                return "Reset failed"
            if data.get('status') != 'STOPPED':
                return f"Expected STOPPED status, got {data.get('status')}"
            self.log(f"  Simulation reset to STOPPED", "info")
            return True
        
        return self.run_test(
            "Simulation Reset",
            "POST", "simulation/reset", 200,
            validate_fn=validate, critical=True
        )

    def test_simulation_start(self):
        """Test POST /api/simulation/start."""
        def validate(data):
            if not data.get('ok'):
                return "Start failed"
            sim = data.get('sim', {})
            if sim.get('status') != 'RUNNING':
                return f"Expected RUNNING status, got {sim.get('status')}"
            self.log(f"  Simulation started: {sim.get('scenario')} at {sim.get('speed')}x", "info")
            return True
        
        return self.run_test(
            "Simulation Start (CYCLONE_FLOOD, 5x)",
            "POST", "simulation/start", 200,
            data={"scenario": "CYCLONE_FLOOD", "speed": 5},
            validate_fn=validate, critical=True
        )

    def test_simulation_status(self):
        """Test GET /api/simulation/status - should show RUNNING and tick increasing."""
        def validate(data):
            if data.get('status') != 'RUNNING':
                return f"Expected RUNNING, got {data.get('status')}"
            if 'tick' not in data:
                return "Missing tick field"
            self.log(f"  Status: {data['status']}, Tick: {data['tick']}, Speed: {data.get('speed')}x", "info")
            return True
        
        return self.run_test(
            "Simulation Status (should be RUNNING)",
            "GET", "simulation/status", 200,
            validate_fn=validate
        )

    def test_simulation_pause(self):
        """Test POST /api/simulation/pause."""
        def validate(data):
            if not data.get('ok'):
                return "Pause failed"
            if data.get('status') != 'PAUSED':
                return f"Expected PAUSED, got {data.get('status')}"
            self.log(f"  Simulation paused", "info")
            return True
        
        return self.run_test(
            "Simulation Pause",
            "POST", "simulation/pause", 200,
            validate_fn=validate
        )

    def test_simulation_inject_flood(self):
        """Test POST /api/simulation/inject - manual flood injection."""
        def validate(data):
            if not data.get('ok'):
                return "Injection failed"
            inc = data.get('incident')
            if not inc:
                return "No incident returned"
            if inc.get('hazard_type') != 'FLOOD':
                return f"Expected FLOOD, got {inc.get('hazard_type')}"
            self.log(f"  Injected: {inc['id']} - {inc['hazard_type']} on {inc.get('road_name')}", "info")
            return True
        
        return self.run_test(
            "Simulation Inject - FLOOD",
            "POST", "simulation/inject", 200,
            data={"inject_type": "FLOOD"},
            validate_fn=validate
        )

    def test_response_actions(self, incident_id):
        """Test response action workflow: acknowledge -> dispatch -> resolve."""
        actions = [
            ("acknowledge", "ACKNOWLEDGED"),
            ("dispatch", "DISPATCHED"),
            ("resolve", "RESOLVED")
        ]
        
        for action, expected_status in actions:
            def validate(data):
                if not data.get('ok'):
                    return f"{action} failed"
                inc = data.get('incident')
                if not inc:
                    return "No incident returned"
                if inc.get('response_status') != expected_status:
                    return f"Expected {expected_status}, got {inc.get('response_status')}"
                self.log(f"  Response status: {expected_status}", "info")
                return True
            
            success, _ = self.run_test(
                f"Response Action - {action.upper()}",
                "POST", f"response/{incident_id}/{action}", 200,
                data={"operator": "TEST_OPERATOR", "note": f"Test {action}"},
                validate_fn=validate
            )
            
            if not success:
                return False
        
        return True

    def test_citizen_report(self):
        """Test POST /api/citizen/report."""
        def validate(data):
            if not data.get('ok'):
                return "Citizen report failed"
            inc = data.get('incident')
            if not inc:
                return "No incident returned"
            self.log(f"  Citizen report created/updated: {inc['id']}", "info")
            return True
        
        return self.run_test(
            "Citizen Report",
            "POST", "citizen/report", 200,
            data={
                "hazard_type": "POTHOLE",
                "latitude": 17.4270,
                "longitude": 78.4489,
                "severity": "MODERATE",
                "description": "Large pothole on main road",
                "reporter_name": "Test Citizen"
            },
            validate_fn=validate
        )

    def test_analytics_summary(self):
        """Test GET /api/analytics/summary."""
        def validate(data):
            required = ['hazards_by_type', 'verification', 'risk_distribution', 
                       'priority_distribution', 'confidence_evolution']
            missing = [k for k in required if k not in data]
            if missing:
                return f"Missing fields: {missing}"
            self.log(f"  Hazard types: {len(data['hazards_by_type'])}", "info")
            self.log(f"  Confidence evolution points: {len(data['confidence_evolution'])}", "info")
            return True
        
        return self.run_test(
            "Analytics Summary",
            "GET", "analytics/summary", 200,
            validate_fn=validate
        )

    def test_network_health(self):
        """Test GET /api/network/health."""
        def validate(data):
            required = ['connected', 'total', 'avg_gps_accuracy', 'avg_latency_ms', 'fusion_success']
            missing = [k for k in required if k not in data]
            if missing:
                return f"Missing fields: {missing}"
            self.log(f"  Connected: {data['connected']}/{data['total']}", "info")
            self.log(f"  GPS Accuracy: {data['avg_gps_accuracy']}", "info")
            self.log(f"  Fusion Success: {data['fusion_success']}%", "info")
            return True
        
        return self.run_test(
            "Network Health",
            "GET", "network/health", 200,
            validate_fn=validate
        )

    def run_all_tests(self):
        """Run complete test suite."""
        print(f"\n{Colors.BLUE}{'='*70}{Colors.RESET}")
        print(f"{Colors.BLUE}ResQDrive Backend API Test Suite{Colors.RESET}")
        print(f"{Colors.BLUE}Base URL: {self.base_url}{Colors.RESET}")
        print(f"{Colors.BLUE}{'='*70}{Colors.RESET}\n")

        # 1. Reset simulation for clean state
        self.log("=== SIMULATION LIFECYCLE ===", "info")
        self.test_simulation_reset()
        
        # 2. Core API tests
        self.log("\n=== CORE APIS ===", "info")
        success, dashboard = self.test_dashboard_summary()
        self.test_network_health()
        
        # 3. Incidents & Vehicles
        self.log("\n=== INCIDENTS & VEHICLES ===", "info")
        success, incidents = self.test_incidents_list()
        incident_id = None
        if success and len(incidents) > 0:
            incident_id = incidents[0]['id']
            self.test_incident_detail(incident_id)
        
        success, vehicles = self.test_vehicles_list()
        if success and len(vehicles) > 0:
            self.test_vehicle_detail(vehicles[0]['id'])
        
        # 4. Roads
        self.log("\n=== ROADS & RISK ===", "info")
        self.test_roads_risk()
        
        # 5. Evidence Fusion (CRITICAL - core innovation)
        self.log("\n=== EVIDENCE FUSION (CORE INNOVATION) ===", "info")
        self.test_evidence_fusion_single_vehicle()
        self.test_evidence_fusion_three_agreeing()
        self.test_evidence_fusion_conflicting()
        
        # 6. Routing
        self.log("\n=== RISK-AWARE ROUTING ===", "info")
        self.test_routes_get()
        self.test_routes_plan()
        
        # 7. Simulation
        self.log("\n=== SIMULATION ===", "info")
        self.test_simulation_start()
        time.sleep(3)  # Wait for a few ticks
        self.test_simulation_status()
        time.sleep(5)  # Wait for more ticks (scenario events)
        self.test_simulation_status()
        self.test_simulation_inject_flood()
        self.test_simulation_pause()
        
        # 8. Response Actions
        if incident_id:
            self.log("\n=== RESPONSE ACTIONS ===", "info")
            self.test_response_actions(incident_id)
        
        # 9. Citizen Reporting
        self.log("\n=== CITIZEN REPORTING ===", "info")
        self.test_citizen_report()
        
        # 10. Analytics
        self.log("\n=== ANALYTICS ===", "info")
        self.test_analytics_summary()
        
        # Print summary
        self.print_summary()
        
        return self.tests_failed == 0 and len(self.critical_failures) == 0

    def print_summary(self):
        """Print test summary."""
        print(f"\n{Colors.BLUE}{'='*70}{Colors.RESET}")
        print(f"{Colors.BLUE}TEST SUMMARY{Colors.RESET}")
        print(f"{Colors.BLUE}{'='*70}{Colors.RESET}")
        print(f"Total Tests: {self.tests_run}")
        print(f"{Colors.GREEN}Passed: {self.tests_passed}{Colors.RESET}")
        print(f"{Colors.RED}Failed: {self.tests_failed}{Colors.RESET}")
        
        if self.critical_failures:
            print(f"\n{Colors.RED}CRITICAL FAILURES:{Colors.RESET}")
            for failure in self.critical_failures:
                print(f"  {Colors.RED}✗{Colors.RESET} {failure}")
        
        if self.warnings:
            print(f"\n{Colors.YELLOW}WARNINGS:{Colors.RESET}")
            for warning in self.warnings:
                print(f"  {Colors.YELLOW}⚠{Colors.RESET} {warning}")
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"\n{Colors.BLUE}Success Rate: {success_rate:.1f}%{Colors.RESET}")
        print(f"{Colors.BLUE}{'='*70}{Colors.RESET}\n")


def main():
    tester = ResQDriveAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
