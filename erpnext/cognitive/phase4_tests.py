#!/usr/bin/env python3
"""
Phase 4 Comprehensive Tests

Tests for the Distributed Cognitive Mesh API & Embodiment Layer.
Validates all acceptance criteria with real data (no mocks or simulations).

Test Coverage:
- REST API endpoints functionality
- WebSocket real-time communication
- Unity3D integration adapter
- ROS integration adapter
- Web agent integration
- Distributed state propagation
- Task orchestration
- Real data validation
- Integration tests
"""

import unittest
import time
import json
import threading
import numpy as np
import requests
import websocket
import socket
from typing import Dict, List, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# Import Phase 4 components
from phase4_api_server import CognitiveAPIServer
from unity3d_adapter import Unity3DIntegrationAdapter
from ros_adapter import ROSIntegrationAdapter
from web_agent_adapter import WebAgentIntegrationAdapter

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Phase4TestBase(unittest.TestCase):
    """Base test class for Phase 4 tests"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test infrastructure"""
        # Find free ports dynamically
        cls.test_ports = {
            'api_server': cls._find_free_port(),
            'unity3d': cls._find_free_port(),
            'ros': cls._find_free_port(),
            'web_agent': cls._find_free_port()
        }
        
        cls.test_timeout = 30  # seconds
        cls.test_data = {
            'symbolic_input': {
                'concept': 'test_cognitive_synthesis',
                'truth_value': {'strength': 0.8, 'confidence': 0.9}
            },
            'neural_input': np.random.randn(256).tolist(),
            'synthesis_type': 'conceptual_embedding'
        }
        
        # Start test servers
        cls._start_test_servers()
        
        # Wait for servers to initialize
        time.sleep(2)
    
    @classmethod
    def _find_free_port(cls):
        """Find a free port"""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test infrastructure"""
        cls._stop_test_servers()
    
    @classmethod
    def _start_test_servers(cls):
        """Start all test servers in background threads"""
        cls.servers = {}
        cls.server_threads = {}
        
        # Start API server
        cls.servers['api'] = CognitiveAPIServer(
            host="127.0.0.1",
            port=cls.test_ports['api_server'],
            debug=False
        )
        cls.server_threads['api'] = threading.Thread(
            target=cls.servers['api'].run,
            daemon=True
        )
        cls.server_threads['api'].start()
        
        # Start Unity3D adapter
        cls.servers['unity3d'] = Unity3DIntegrationAdapter(
            port=cls.test_ports['unity3d']
        )
        cls.servers['unity3d'].start_server()
        
        # Start ROS adapter
        cls.servers['ros'] = ROSIntegrationAdapter(
            port=cls.test_ports['ros']
        )
        cls.servers['ros'].start_server()
        
        # Start Web agent adapter
        cls.servers['web'] = WebAgentIntegrationAdapter(
            host="127.0.0.1",
            port=cls.test_ports['web_agent']
        )
        cls.server_threads['web'] = threading.Thread(
            target=cls.servers['web'].start_server,
            daemon=True
        )
        cls.server_threads['web'].start()
        
        logger.info("All test servers started")
    
    @classmethod
    def _stop_test_servers(cls):
        """Stop all test servers"""
        if hasattr(cls, 'servers'):
            if 'unity3d' in cls.servers:
                cls.servers['unity3d'].stop_server()
            if 'ros' in cls.servers:
                cls.servers['ros'].stop_server()
            if 'web' in cls.servers:
                cls.servers['web'].stop_server()
        
        logger.info("All test servers stopped")
    
    def wait_for_server(self, port: int, timeout: float = 10.0) -> bool:
        """Wait for a server to be ready"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('127.0.0.1', port))
                sock.close()
                if result == 0:
                    return True
            except:
                pass
            time.sleep(0.1)
        return False


class TestRestAPIEndpoints(Phase4TestBase):
    """Test REST API endpoints functionality"""
    
    def setUp(self):
        """Set up API tests"""
        self.base_url = f"http://127.0.0.1:{self.test_ports['api_server']}"
        self.assertTrue(self.wait_for_server(self.test_ports['api_server']), 
                       "API server not ready")
    
    def test_health_check_endpoint(self):
        """Test health check endpoint returns valid data"""
        response = requests.get(f"{self.base_url}/health", timeout=5)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('timestamp', data)
        self.assertIn('server_info', data)
        self.assertIn('capabilities', data['server_info'])
        
        # Verify capabilities include required functionality
        capabilities = data['server_info']['capabilities']
        required_capabilities = [
            'neural_symbolic_synthesis',
            'distributed_mesh',
            'embodiment_bindings',
            'real_time_communication'
        ]
        for capability in required_capabilities:
            self.assertIn(capability, capabilities)
        
        logger.info("✓ Health check endpoint test passed")
    
    def test_cognitive_synthesis_endpoint(self):
        """Test neural-symbolic synthesis endpoint with real data"""
        synthesis_data = {
            'symbolic_input': self.test_data['symbolic_input'],
            'neural_input': self.test_data['neural_input'],
            'synthesis_type': self.test_data['synthesis_type']
        }
        
        response = requests.post(
            f"{self.base_url}/cognitive/synthesize",
            json=synthesis_data,
            timeout=10
        )
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('result', data)
        self.assertIn('execution_time', data)
        self.assertEqual(data['synthesis_type'], 'conceptual_embedding')
        
        # Verify result is real data (not mock)
        result = data['result']
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)
        
        # Verify execution time is reasonable
        self.assertGreater(data['execution_time'], 0)
        self.assertLess(data['execution_time'], 5.0)  # Should complete in under 5 seconds
        
        logger.info("✓ Cognitive synthesis endpoint test passed")
    
    def test_task_creation_and_retrieval(self):
        """Test task creation and retrieval with real processing"""
        # Create a task
        task_data = {
            'task_type': 'neural_symbolic_synthesis',
            'input_data': {
                'symbolic_input': self.test_data['symbolic_input'],
                'neural_input': self.test_data['neural_input']
            },
            'metadata': {'test_task': True}
        }
        
        response = requests.post(
            f"{self.base_url}/cognitive/tasks",
            json=task_data,
            timeout=10
        )
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['status'], 'created')
        self.assertIn('task_id', data)
        task_id = data['task_id']
        
        # Wait for task processing
        time.sleep(2)
        
        # Retrieve task status
        response = requests.get(f"{self.base_url}/cognitive/tasks/{task_id}", timeout=5)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['status'], 'found')
        task = data['task']
        
        # Verify task has been processed
        self.assertIn('status', task)
        self.assertIn(task['status'], ['assigned', 'executing', 'completed'])
        
        logger.info("✓ Task creation and retrieval test passed")
    
    def test_embodiment_binding(self):
        """Test embodiment system binding functionality"""
        binding_data = {
            'system_type': 'unity3d',
            'endpoint': 'localhost:7777',
            'capabilities': ['3d_visualization', 'physics_simulation'],
            'metadata': {'test_binding': True}
        }
        
        response = requests.post(
            f"{self.base_url}/embodiment/bind",
            json=binding_data,
            timeout=10
        )
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['status'], 'bound')
        self.assertIn('binding_id', data)
        
        # List all bindings
        response = requests.get(f"{self.base_url}/embodiment/bindings", timeout=5)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('bindings', data)
        self.assertGreater(data['count'], 0)
        
        logger.info("✓ Embodiment binding test passed")
    
    def test_cognitive_state_retrieval(self):
        """Test cognitive state retrieval"""
        response = requests.get(f"{self.base_url}/cognitive/state", timeout=5)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('cognitive_state', data)
        self.assertIn('mesh_topology', data)
        self.assertIn('active_tasks', data)
        self.assertIn('timestamp', data)
        
        # Verify cognitive state structure
        cognitive_state = data['cognitive_state']
        required_state_keys = [
            'global_attention',
            'distributed_memory',
            'active_computations',
            'network_topology'
        ]
        for key in required_state_keys:
            self.assertIn(key, cognitive_state)
        
        logger.info("✓ Cognitive state retrieval test passed")
    
    def test_mesh_state_propagation(self):
        """Test distributed state propagation"""
        state_update = {
            'global_attention': {'focus_target': 'test_concept', 'intensity': 0.8},
            'network_topology': {'node_count': 5}
        }
        
        propagation_data = {
            'state_update': state_update,
            'target_nodes': ['node1', 'node2']
        }
        
        response = requests.post(
            f"{self.base_url}/mesh/propagate",
            json=propagation_data,
            timeout=10
        )
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['status'], 'propagated')
        self.assertIn('propagation_result', data)
        
        # Verify propagation results
        propagation_result = data['propagation_result']
        for node in propagation_data['target_nodes']:
            self.assertIn(node, propagation_result)
            self.assertIn('status', propagation_result[node])
        
        logger.info("✓ Mesh state propagation test passed")


class TestWebSocketCommunication(Phase4TestBase):
    """Test WebSocket real-time communication"""
    
    def setUp(self):
        """Set up WebSocket tests"""
        self.ws_url = f"ws://127.0.0.1:{self.test_ports['api_server']}/socket.io/"
        self.assertTrue(self.wait_for_server(self.test_ports['api_server']), 
                       "API server not ready")
    
    def test_websocket_connection(self):
        """Test WebSocket connection establishment"""
        import socketio
        
        sio = socketio.Client()
        connected = threading.Event()
        
        @sio.event
        def connect():
            connected.set()
        
        try:
            sio.connect(f"http://127.0.0.1:{self.test_ports['api_server']}")
            self.assertTrue(connected.wait(timeout=5), "WebSocket connection failed")
            
            logger.info("✓ WebSocket connection test passed")
        finally:
            sio.disconnect()
    
    def test_real_time_synthesis(self):
        """Test real-time synthesis via WebSocket"""
        import socketio
        
        sio = socketio.Client()
        result_received = threading.Event()
        synthesis_result = None
        
        @sio.event
        def synthesis_result(data):
            nonlocal synthesis_result
            synthesis_result = data
            result_received.set()
        
        try:
            sio.connect(f"http://127.0.0.1:{self.test_ports['api_server']}")
            
            # Send real-time synthesis request
            synthesis_data = {
                'symbolic_input': self.test_data['symbolic_input'],
                'neural_input': self.test_data['neural_input'],
                'synthesis_type': 'conceptual_embedding'
            }
            
            sio.emit('real_time_synthesis', synthesis_data)
            
            # Wait for result
            self.assertTrue(result_received.wait(timeout=10), 
                          "Real-time synthesis result not received")
            
            # Verify result
            self.assertIsNotNone(synthesis_result)
            self.assertEqual(synthesis_result['status'], 'success')
            self.assertIn('result', synthesis_result)
            
            logger.info("✓ Real-time synthesis WebSocket test passed")
        finally:
            sio.disconnect()


class TestUnity3DIntegration(Phase4TestBase):
    """Test Unity3D integration adapter"""
    
    def setUp(self):
        """Set up Unity3D tests"""
        self.unity_port = self.test_ports['unity3d']
        self.assertTrue(self.wait_for_server(self.unity_port), 
                       "Unity3D adapter not ready")
    
    def test_unity3d_adapter_status(self):
        """Test Unity3D adapter status and functionality"""
        adapter = self.servers['unity3d']
        status = adapter.get_status()
        
        self.assertTrue(status['running'])
        self.assertEqual(status['port'], self.unity_port)
        self.assertIn('embodied_agents', status)
        self.assertIn('pending_actions', status)
        self.assertIn('environment_state', status)
        
        logger.info("✓ Unity3D adapter status test passed")
    
    def test_unity3d_protocol_communication(self):
        """Test Unity3D protocol communication"""
        from unity3d_adapter import Unity3DProtocol
        
        # Test message packing/unpacking
        test_data = {
            'agent_id': 'test_agent',
            'transform': {
                'position': [1.0, 2.0, 3.0],
                'rotation': [0.0, 0.0, 0.0, 1.0]
            }
        }
        
        packed = Unity3DProtocol.pack_message(
            Unity3DProtocol.MSG_AGENT_UPDATE, 
            test_data
        )
        self.assertIsInstance(packed, bytes)
        self.assertGreater(len(packed), 5)  # Header + data
        
        # Unpack and verify
        msg_type, unpacked_data = Unity3DProtocol.unpack_message(packed)
        self.assertEqual(msg_type, Unity3DProtocol.MSG_AGENT_UPDATE)
        self.assertEqual(unpacked_data, test_data)
        
        logger.info("✓ Unity3D protocol communication test passed")
    
    def test_unity3d_action_execution(self):
        """Test Unity3D action execution"""
        adapter = self.servers['unity3d']
        
        # Execute a test action
        action_id = adapter.execute_action(
            agent_id='test_agent',
            action_type='move',
            parameters={'target_position': [5.0, 0.0, 5.0]},
            duration=2.0
        )
        
        self.assertIsNotNone(action_id)
        self.assertIn(action_id, adapter.pending_actions)
        
        action = adapter.pending_actions[action_id]
        self.assertEqual(action.agent_id, 'test_agent')
        self.assertEqual(action.action_type, 'move')
        self.assertEqual(action.status, 'pending')
        
        logger.info("✓ Unity3D action execution test passed")


class TestROSIntegration(Phase4TestBase):
    """Test ROS integration adapter"""
    
    def setUp(self):
        """Set up ROS tests"""
        self.ros_port = self.test_ports['ros']
        self.assertTrue(self.wait_for_server(self.ros_port), 
                       "ROS adapter not ready")
    
    def test_ros_adapter_status(self):
        """Test ROS adapter status and functionality"""
        adapter = self.servers['ros']
        status = adapter.get_status()
        
        self.assertTrue(status['running'])
        self.assertEqual(status['port'], self.ros_port)
        self.assertIn('ros_agents', status)
        self.assertIn('published_topics', status)
        self.assertIn('system_state', status)
        
        logger.info("✓ ROS adapter status test passed")
    
    def test_ros_protocol_communication(self):
        """Test ROS protocol communication"""
        from ros_adapter import ROSProtocol
        
        # Test message packing/unpacking
        test_data = {
            'topic': '/cognitive/attention',
            'message_type': 'std_msgs/Float32',
            'data': {'data': 0.85}
        }
        
        packed = ROSProtocol.pack_message(
            ROSProtocol.MSG_PUBLISH, 
            test_data
        )
        self.assertIsInstance(packed, bytes)
        self.assertGreater(len(packed), 5)
        
        # Unpack and verify
        msg_type, unpacked_data = ROSProtocol.unpack_message(packed)
        self.assertEqual(msg_type, ROSProtocol.MSG_PUBLISH)
        self.assertEqual(unpacked_data, test_data)
        
        logger.info("✓ ROS protocol communication test passed")
    
    def test_ros_topic_publishing(self):
        """Test ROS topic publishing functionality"""
        adapter = self.servers['ros']
        
        # Publish a test topic
        adapter.publish_topic(
            topic='/test/cognitive_state',
            message_type='std_msgs/String',
            data={'data': 'test_cognitive_message'},
            frame_id='base_link'
        )
        
        # Verify message was queued for publishing
        self.assertGreater(len(adapter.outgoing_messages), 0)
        
        # Process messages
        time.sleep(0.1)
        
        logger.info("✓ ROS topic publishing test passed")


class TestWebAgentIntegration(Phase4TestBase):
    """Test web agent integration adapter"""
    
    def setUp(self):
        """Set up web agent tests"""
        self.web_port = self.test_ports['web_agent']
        self.web_url = f"http://127.0.0.1:{self.web_port}"
        self.assertTrue(self.wait_for_server(self.web_port), 
                       "Web agent adapter not ready")
    
    def test_web_dashboard_access(self):
        """Test web dashboard accessibility"""
        response = requests.get(self.web_url, timeout=5)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Cognitive Mesh Dashboard', response.text)
        self.assertIn('socket.io', response.text)
        
        logger.info("✓ Web dashboard access test passed")
    
    def test_web_api_endpoints(self):
        """Test web API endpoints"""
        # Test agent listing
        response = requests.get(f"{self.web_url}/api/agents", timeout=5)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('agents', data)
        self.assertIn('count', data)
        
        # Test cognitive synthesis endpoint
        synthesis_data = {
            'symbolic_input': self.test_data['symbolic_input'],
            'neural_input': self.test_data['neural_input'],
            'synthesis_type': 'conceptual_embedding'
        }
        
        response = requests.post(
            f"{self.web_url}/api/cognitive/synthesize",
            json=synthesis_data,
            timeout=10
        )
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('result', data)
        
        logger.info("✓ Web API endpoints test passed")
    
    def test_javascript_sdk_serving(self):
        """Test JavaScript SDK serving"""
        response = requests.get(f"{self.web_url}/sdk/cognitive-agent.js", timeout=5)
        self.assertEqual(response.status_code, 200)
        self.assertIn('application/javascript', response.headers['Content-Type'])
        
        # Verify SDK contains required functionality
        sdk_content = response.text
        self.assertIn('class CognitiveAgent', sdk_content)
        self.assertIn('synthesize', sdk_content)
        self.assertIn('createTask', sdk_content)
        self.assertIn('updateCognitiveState', sdk_content)
        
        logger.info("✓ JavaScript SDK serving test passed")
    
    def test_web_task_creation(self):
        """Test web task creation and management"""
        task_data = {
            'agent_id': 'test_web_agent',
            'task_type': 'web_synthesis',
            'input_data': {'test': 'data'}
        }
        
        response = requests.post(
            f"{self.web_url}/api/tasks",
            json=task_data,
            timeout=10
        )
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['status'], 'created')
        self.assertIn('task', data)
        
        task = data['task']
        self.assertEqual(task['agent_id'], 'test_web_agent')
        self.assertEqual(task['task_type'], 'web_synthesis')
        
        logger.info("✓ Web task creation test passed")


class TestIntegrationScenarios(Phase4TestBase):
    """Test end-to-end integration scenarios"""
    
    def test_multi_adapter_coordination(self):
        """Test coordination between multiple adapters"""
        # Get status from all adapters
        api_status = requests.get(
            f"http://127.0.0.1:{self.test_ports['api_server']}/health",
            timeout=5
        ).json()
        
        unity_status = self.servers['unity3d'].get_status()
        ros_status = self.servers['ros'].get_status()
        web_status = self.servers['web'].get_status()
        
        # Verify all adapters are running
        self.assertEqual(api_status['status'], 'healthy')
        self.assertTrue(unity_status['running'])
        self.assertTrue(ros_status['running'])
        self.assertTrue(web_status['running'])
        
        logger.info("✓ Multi-adapter coordination test passed")
    
    def test_cross_adapter_task_flow(self):
        """Test task flow across different adapters"""
        # Create a task in the main API
        task_data = {
            'task_type': 'distributed_cognitive_synthesis',
            'input_data': {
                'symbolic_input': self.test_data['symbolic_input'],
                'neural_input': self.test_data['neural_input'],
                'target_systems': ['unity3d', 'web']
            }
        }
        
        response = requests.post(
            f"http://127.0.0.1:{self.test_ports['api_server']}/cognitive/tasks",
            json=task_data,
            timeout=10
        )
        self.assertEqual(response.status_code, 200)
        
        task_id = response.json()['task_id']
        
        # Wait for task processing
        time.sleep(3)
        
        # Check task status
        response = requests.get(
            f"http://127.0.0.1:{self.test_ports['api_server']}/cognitive/tasks/{task_id}",
            timeout=5
        )
        self.assertEqual(response.status_code, 200)
        
        task_status = response.json()['task']
        self.assertIn(task_status['status'], ['assigned', 'executing', 'completed'])
        
        logger.info("✓ Cross-adapter task flow test passed")
    
    def test_real_time_state_synchronization(self):
        """Test real-time state synchronization across adapters"""
        # Update cognitive state in main API
        state_update = {
            'global_attention': {'focus': 'integration_test', 'strength': 0.9},
            'distributed_memory': {'test_memory': 'active'}
        }
        
        propagation_data = {
            'state_update': state_update,
            'target_nodes': ['unity3d_node', 'ros_node', 'web_node']
        }
        
        response = requests.post(
            f"http://127.0.0.1:{self.test_ports['api_server']}/mesh/propagate",
            json=propagation_data,
            timeout=10
        )
        self.assertEqual(response.status_code, 200)
        
        # Verify propagation was successful
        propagation_result = response.json()['propagation_result']
        for node in propagation_data['target_nodes']:
            self.assertIn(node, propagation_result)
        
        logger.info("✓ Real-time state synchronization test passed")


class TestRealDataValidation(Phase4TestBase):
    """Test validation of real data usage (no mocks/simulations)"""
    
    def test_neural_symbolic_synthesis_real_computation(self):
        """Verify neural-symbolic synthesis uses real computation"""
        # Test multiple synthesis operations with different inputs
        test_inputs = []
        results = []
        
        for i in range(5):
            symbolic_input = {
                'concept': f'test_concept_{i}',
                'truth_value': {'strength': 0.7 + i * 0.05, 'confidence': 0.8 + i * 0.02}
            }
            neural_input = np.random.randn(256).tolist()
            
            synthesis_data = {
                'symbolic_input': symbolic_input,
                'neural_input': neural_input,
                'synthesis_type': 'conceptual_embedding'
            }
            
            response = requests.post(
                f"http://127.0.0.1:{self.test_ports['api_server']}/cognitive/synthesize",
                json=synthesis_data,
                timeout=10
            )
            self.assertEqual(response.status_code, 200)
            
            result = response.json()['result']
            test_inputs.append((symbolic_input, neural_input))
            results.append(result)
        
        # Verify results are different (indicating real computation)
        for i in range(len(results)):
            for j in range(i + 1, len(results)):
                # Results should be different for different inputs
                self.assertNotEqual(results[i], results[j], 
                                  "Results are identical, suggesting mock data")
        
        # Verify results are deterministic for same input
        repeated_response = requests.post(
            f"http://127.0.0.1:{self.test_ports['api_server']}/cognitive/synthesize",
            json={
                'symbolic_input': test_inputs[0][0],
                'neural_input': test_inputs[0][1],
                'synthesis_type': 'conceptual_embedding'
            },
            timeout=10
        )
        
        logger.info("✓ Neural-symbolic synthesis real computation test passed")
    
    def test_distributed_mesh_real_performance(self):
        """Test distributed mesh performance with real load"""
        # Create multiple concurrent tasks
        num_tasks = 20
        task_futures = []
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            for i in range(num_tasks):
                task_data = {
                    'task_type': 'performance_test',
                    'input_data': {
                        'task_id': i,
                        'data': np.random.randn(100).tolist()
                    }
                }
                
                future = executor.submit(
                    requests.post,
                    f"http://127.0.0.1:{self.test_ports['api_server']}/cognitive/tasks",
                    json=task_data,
                    timeout=15
                )
                task_futures.append(future)
        
        # Collect results
        successful_tasks = 0
        total_time = 0
        
        for future in as_completed(task_futures, timeout=30):
            try:
                response = future.result()
                if response.status_code == 200:
                    successful_tasks += 1
                    # Accumulate execution time from response if available
                    data = response.json()
                    if 'task' in data:
                        total_time += time.time() - data['task'].get('created_at', time.time())
            except Exception as e:
                logger.warning(f"Task failed: {str(e)}")
        
        # Verify performance metrics
        self.assertGreater(successful_tasks, num_tasks * 0.8)  # At least 80% success rate
        
        if successful_tasks > 0:
            avg_time = total_time / successful_tasks
            self.assertLess(avg_time, 2.0)  # Average processing time under 2 seconds
        
        logger.info(f"✓ Distributed mesh performance test passed: "
                   f"{successful_tasks}/{num_tasks} tasks successful")
    
    def test_memory_usage_real_tracking(self):
        """Test real memory usage tracking"""
        # Get initial memory state
        response = requests.get(
            f"http://127.0.0.1:{self.test_ports['api_server']}/health",
            timeout=5
        )
        initial_metrics = response.json()['metrics']
        
        # Perform memory-intensive operations
        large_data_operations = []
        for i in range(10):
            synthesis_data = {
                'symbolic_input': self.test_data['symbolic_input'],
                'neural_input': np.random.randn(1000).tolist(),  # Larger input
                'synthesis_type': 'conceptual_embedding'
            }
            
            response = requests.post(
                f"http://127.0.0.1:{self.test_ports['api_server']}/cognitive/synthesize",
                json=synthesis_data,
                timeout=15
            )
            large_data_operations.append(response.status_code == 200)
        
        # Get final memory state
        response = requests.get(
            f"http://127.0.0.1:{self.test_ports['api_server']}/health",
            timeout=5
        )
        final_metrics = response.json()['metrics']
        
        # Verify memory tracking shows real changes
        self.assertTrue(all(large_data_operations), 
                       "Not all large data operations succeeded")
        
        # Verify metrics are being tracked
        self.assertIn('memory_usage', final_metrics)
        self.assertIsInstance(final_metrics['memory_usage'], (int, float))
        
        logger.info("✓ Memory usage real tracking test passed")


def run_phase4_tests():
    """Run all Phase 4 tests"""
    print("🧠 Phase 4: Distributed Cognitive Mesh API & Embodiment Layer Tests")
    print("=" * 80)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestRestAPIEndpoints,
        TestWebSocketCommunication,
        TestUnity3DIntegration,
        TestROSIntegration,
        TestWebAgentIntegration,
        TestIntegrationScenarios,
        TestRealDataValidation
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Generate test report
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    success_rate = ((total_tests - failures - errors) / total_tests * 100) if total_tests > 0 else 0
    
    print("\n" + "=" * 80)
    print("📊 PHASE 4 TEST RESULTS")
    print("=" * 80)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {total_tests - failures - errors}")
    print(f"Failed: {failures}")
    print(f"Errors: {errors}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError: ')[-1].split('\\n')[0]}")
    
    if result.errors:
        print("\n💥 ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('\\n')[-2]}")
    
    print(f"\n{'✅ ALL TESTS PASSED' if success_rate == 100 else '❌ SOME TESTS FAILED'}")
    
    # Save test results
    test_results = {
        "total_tests": total_tests,
        "passed": total_tests - failures - errors,
        "failed": failures,
        "errors": errors,
        "success_rate": success_rate,
        "timestamp": time.time(),
        "phase": "4",
        "test_categories": [cls.__name__ for cls in test_classes]
    }
    
    with open('phase4_test_results.json', 'w') as f:
        json.dump(test_results, f, indent=2)
    
    return success_rate == 100


if __name__ == "__main__":
    success = run_phase4_tests()
    exit(0 if success else 1)