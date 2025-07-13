#!/usr/bin/env python3
"""
Unity3D Embodiment Integration Adapter

Provides Unity3D-specific integration for the distributed cognitive mesh.
Handles bidirectional communication with Unity3D engines for embodied cognition.

Key Features:
- Unity3D-compatible data serialization
- Real-time position and orientation updates
- Cognitive state mapping to Unity GameObject properties
- Action execution in Unity environments
- Sensor data ingestion from Unity scenes
"""

import json
import time
import threading
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import socket
import struct
import logging
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


@dataclass
class Unity3DTransform:
    """Unity3D Transform component representation"""
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 1.0)  # Quaternion
    scale: Tuple[float, float, float] = (1.0, 1.0, 1.0)


@dataclass
class Unity3DCognitiveAgent:
    """Represents a cognitive agent embodied in Unity3D"""
    agent_id: str
    game_object_name: str
    transform: Unity3DTransform
    cognitive_state: Dict[str, Any]
    capabilities: List[str]
    sensors: Dict[str, Any]
    actuators: Dict[str, Any]
    last_update: float = 0.0

    def __post_init__(self):
        if self.last_update == 0.0:
            self.last_update = time.time()


@dataclass
class Unity3DAction:
    """Action to be executed in Unity3D environment"""
    action_id: str
    agent_id: str
    action_type: str  # "move", "rotate", "interact", "speak", etc.
    parameters: Dict[str, Any]
    duration: float = 0.0
    status: str = "pending"
    created_at: float = 0.0

    def __post_init__(self):
        if self.created_at == 0.0:
            self.created_at = time.time()


class Unity3DProtocol:
    """Protocol handler for Unity3D communication"""
    
    # Message types
    MSG_HANDSHAKE = 0x01
    MSG_AGENT_UPDATE = 0x02
    MSG_ACTION_REQUEST = 0x03
    MSG_ACTION_RESPONSE = 0x04
    MSG_SENSOR_DATA = 0x05
    MSG_COGNITIVE_STATE = 0x06
    MSG_HEARTBEAT = 0x07
    
    @staticmethod
    def pack_message(msg_type: int, data: Dict[str, Any]) -> bytes:
        """Pack a message for Unity3D transmission"""
        json_data = json.dumps(data).encode('utf-8')
        header = struct.pack('!BI', msg_type, len(json_data))
        return header + json_data
    
    @staticmethod
    def unpack_message(data: bytes) -> Tuple[int, Dict[str, Any]]:
        """Unpack a message from Unity3D"""
        if len(data) < 5:  # Header size
            raise ValueError("Message too short")
        
        msg_type, data_length = struct.unpack('!BI', data[:5])
        json_data = data[5:5+data_length].decode('utf-8')
        
        return msg_type, json.loads(json_data)


class Unity3DIntegrationAdapter:
    """Main adapter for Unity3D embodiment integration"""
    
    def __init__(self, port: int = 7777, host: str = '127.0.0.1', max_agents: int = 100):
        self.port = port
        self.host = host
        self.max_agents = max_agents
        
        # Connection management
        self.server_socket = None
        self.client_connections: Dict[str, socket.socket] = {}
        self.connection_threads: Dict[str, threading.Thread] = {}
        
        # Agent management
        self.embodied_agents: Dict[str, Unity3DCognitiveAgent] = {}
        self.pending_actions: Dict[str, Unity3DAction] = {}
        
        # State management
        self.unity_environment_state = {
            "scene_name": "",
            "objects": {},
            "lighting": {},
            "physics": {}
        }
        
        # Communication queues
        self.outgoing_messages = []
        self.incoming_messages = []
        
        self.running = False
        self.executor = ThreadPoolExecutor(max_workers=20)
        
        logger.info("Unity3D Integration Adapter initialized")
    
    def start_server(self):
        """Start the Unity3D integration server"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        
        self.running = True
        
        # Start connection acceptor thread
        threading.Thread(target=self._accept_connections, daemon=True).start()
        
        # Start message processor thread
        threading.Thread(target=self._process_messages, daemon=True).start()
        
        logger.info(f"Unity3D server started on port {self.port}")
    
    def stop_server(self):
        """Stop the Unity3D integration server"""
        self.running = False
        
        # Close all client connections
        for conn_id, conn in self.client_connections.items():
            try:
                conn.close()
            except:
                pass
        
        # Close server socket
        if self.server_socket:
            self.server_socket.close()
        
        logger.info("Unity3D server stopped")
    
    def _accept_connections(self):
        """Accept incoming Unity3D connections"""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                connection_id = f"unity_{address[0]}_{address[1]}_{int(time.time())}"
                
                self.client_connections[connection_id] = client_socket
                
                # Start handler thread for this connection
                handler_thread = threading.Thread(
                    target=self._handle_client,
                    args=(connection_id, client_socket),
                    daemon=True
                )
                handler_thread.start()
                self.connection_threads[connection_id] = handler_thread
                
                logger.info(f"New Unity3D connection: {connection_id} from {address}")
                
                # Send handshake
                handshake_msg = Unity3DProtocol.pack_message(
                    Unity3DProtocol.MSG_HANDSHAKE,
                    {
                        "connection_id": connection_id,
                        "server_version": "1.0.0",
                        "capabilities": [
                            "cognitive_agent_control",
                            "real_time_updates",
                            "sensor_data_streaming",
                            "action_execution"
                        ],
                        "timestamp": time.time()
                    }
                )
                client_socket.send(handshake_msg)
                
            except Exception as e:
                if self.running:
                    logger.error(f"Connection accept error: {str(e)}")
                break
    
    def _handle_client(self, connection_id: str, client_socket: socket.socket):
        """Handle communication with a Unity3D client"""
        buffer = b""
        
        while self.running:
            try:
                data = client_socket.recv(4096)
                if not data:
                    break
                
                buffer += data
                
                # Process complete messages in buffer
                while len(buffer) >= 5:  # Minimum header size
                    try:
                        msg_type, data_length = struct.unpack('!BI', buffer[:5])
                        total_length = 5 + data_length
                        
                        if len(buffer) < total_length:
                            break  # Wait for more data
                        
                        # Extract complete message
                        message_data = buffer[:total_length]
                        buffer = buffer[total_length:]
                        
                        # Process message
                        self._process_unity_message(connection_id, message_data)
                        
                    except Exception as e:
                        logger.error(f"Message processing error: {str(e)}")
                        break
                
            except Exception as e:
                logger.error(f"Client handling error: {str(e)}")
                break
        
        # Cleanup connection
        self._cleanup_connection(connection_id)
    
    def _process_unity_message(self, connection_id: str, message_data: bytes):
        """Process a message from Unity3D"""
        try:
            msg_type, data = Unity3DProtocol.unpack_message(message_data)
            
            if msg_type == Unity3DProtocol.MSG_AGENT_UPDATE:
                self._handle_agent_update(connection_id, data)
            elif msg_type == Unity3DProtocol.MSG_ACTION_RESPONSE:
                self._handle_action_response(connection_id, data)
            elif msg_type == Unity3DProtocol.MSG_SENSOR_DATA:
                self._handle_sensor_data(connection_id, data)
            elif msg_type == Unity3DProtocol.MSG_HEARTBEAT:
                self._handle_heartbeat(connection_id, data)
            else:
                logger.warning(f"Unknown message type: {msg_type}")
                
        except Exception as e:
            logger.error(f"Unity message processing error: {str(e)}")
    
    def _handle_agent_update(self, connection_id: str, data: Dict[str, Any]):
        """Handle agent state update from Unity3D"""
        agent_id = data.get('agent_id')
        if not agent_id:
            return
        
        # Update or create agent
        if agent_id not in self.embodied_agents:
            self.embodied_agents[agent_id] = Unity3DCognitiveAgent(
                agent_id=agent_id,
                game_object_name=data.get('game_object_name', f"CognitiveAgent_{agent_id}"),
                transform=Unity3DTransform(),
                cognitive_state={},
                capabilities=data.get('capabilities', []),
                sensors={},
                actuators={}
            )
        
        agent = self.embodied_agents[agent_id]
        
        # Update transform
        if 'transform' in data:
            transform_data = data['transform']
            agent.transform.position = tuple(transform_data.get('position', [0, 0, 0]))
            agent.transform.rotation = tuple(transform_data.get('rotation', [0, 0, 0, 1]))
            agent.transform.scale = tuple(transform_data.get('scale', [1, 1, 1]))
        
        # Update cognitive state
        if 'cognitive_state' in data:
            agent.cognitive_state.update(data['cognitive_state'])
        
        # Update sensors
        if 'sensors' in data:
            agent.sensors.update(data['sensors'])
        
        agent.last_update = time.time()
        
        logger.debug(f"Updated Unity3D agent: {agent_id}")
    
    def _handle_action_response(self, connection_id: str, data: Dict[str, Any]):
        """Handle action execution response from Unity3D"""
        action_id = data.get('action_id')
        if action_id not in self.pending_actions:
            return
        
        action = self.pending_actions[action_id]
        action.status = data.get('status', 'completed')
        
        if action.status == 'completed':
            del self.pending_actions[action_id]
        
        logger.debug(f"Action {action_id} status: {action.status}")
    
    def _handle_sensor_data(self, connection_id: str, data: Dict[str, Any]):
        """Handle sensor data from Unity3D"""
        agent_id = data.get('agent_id')
        sensor_type = data.get('sensor_type')
        sensor_data = data.get('data', {})
        
        if agent_id in self.embodied_agents:
            agent = self.embodied_agents[agent_id]
            agent.sensors[sensor_type] = {
                'data': sensor_data,
                'timestamp': time.time()
            }
        
        logger.debug(f"Received sensor data: {sensor_type} from agent {agent_id}")
    
    def _handle_heartbeat(self, connection_id: str, data: Dict[str, Any]):
        """Handle heartbeat from Unity3D"""
        # Update environment state if provided
        if 'environment_state' in data:
            self.unity_environment_state.update(data['environment_state'])
        
        # Send heartbeat response
        response = Unity3DProtocol.pack_message(
            Unity3DProtocol.MSG_HEARTBEAT,
            {
                "status": "alive",
                "timestamp": time.time(),
                "active_agents": len(self.embodied_agents)
            }
        )
        
        if connection_id in self.client_connections:
            try:
                self.client_connections[connection_id].send(response)
            except Exception as e:
                logger.error(f"Heartbeat response error: {str(e)}")
    
    def _cleanup_connection(self, connection_id: str):
        """Clean up a disconnected connection"""
        if connection_id in self.client_connections:
            del self.client_connections[connection_id]
        
        if connection_id in self.connection_threads:
            del self.connection_threads[connection_id]
        
        logger.info(f"Cleaned up Unity3D connection: {connection_id}")
    
    def _process_messages(self):
        """Process outgoing messages to Unity3D"""
        while self.running:
            try:
                if self.outgoing_messages:
                    message = self.outgoing_messages.pop(0)
                    self._send_message_to_unity(message)
                
                time.sleep(0.01)  # Small delay to prevent busy waiting
                
            except Exception as e:
                logger.error(f"Message processing error: {str(e)}")
    
    def _send_message_to_unity(self, message: Dict[str, Any]):
        """Send a message to Unity3D clients"""
        target_connection = message.get('target_connection')
        msg_type = message.get('msg_type')
        data = message.get('data', {})
        
        packed_message = Unity3DProtocol.pack_message(msg_type, data)
        
        if target_connection and target_connection in self.client_connections:
            # Send to specific connection
            try:
                self.client_connections[target_connection].send(packed_message)
            except Exception as e:
                logger.error(f"Send message error: {str(e)}")
        else:
            # Broadcast to all connections
            for conn_id, conn in self.client_connections.items():
                try:
                    conn.send(packed_message)
                except Exception as e:
                    logger.error(f"Broadcast error to {conn_id}: {str(e)}")
    
    def send_cognitive_state_update(self, agent_id: str, cognitive_state: Dict[str, Any]):
        """Send cognitive state update to Unity3D"""
        message = {
            'msg_type': Unity3DProtocol.MSG_COGNITIVE_STATE,
            'data': {
                'agent_id': agent_id,
                'cognitive_state': cognitive_state,
                'timestamp': time.time()
            }
        }
        self.outgoing_messages.append(message)
    
    def execute_action(self, agent_id: str, action_type: str, 
                      parameters: Dict[str, Any], duration: float = 0.0) -> str:
        """Execute an action in Unity3D"""
        action_id = f"action_{agent_id}_{int(time.time() * 1000)}"
        
        action = Unity3DAction(
            action_id=action_id,
            agent_id=agent_id,
            action_type=action_type,
            parameters=parameters,
            duration=duration
        )
        
        self.pending_actions[action_id] = action
        
        # Send action request to Unity3D
        message = {
            'msg_type': Unity3DProtocol.MSG_ACTION_REQUEST,
            'data': {
                'action_id': action_id,
                'agent_id': agent_id,
                'action_type': action_type,
                'parameters': parameters,
                'duration': duration,
                'timestamp': time.time()
            }
        }
        self.outgoing_messages.append(message)
        
        return action_id
    
    def get_agent_state(self, agent_id: str) -> Optional[Unity3DCognitiveAgent]:
        """Get the current state of an embodied agent"""
        return self.embodied_agents.get(agent_id)
    
    def list_agents(self) -> List[Unity3DCognitiveAgent]:
        """List all embodied agents"""
        return list(self.embodied_agents.values())
    
    def get_environment_state(self) -> Dict[str, Any]:
        """Get current Unity3D environment state"""
        return self.unity_environment_state.copy()
    
    def update_agent_transform(self, agent_id: str, position: Optional[Tuple[float, float, float]] = None,
                              rotation: Optional[Tuple[float, float, float, float]] = None,
                              scale: Optional[Tuple[float, float, float]] = None):
        """Update an agent's transform in Unity3D"""
        if agent_id not in self.embodied_agents:
            return
        
        agent = self.embodied_agents[agent_id]
        
        if position:
            agent.transform.position = position
        if rotation:
            agent.transform.rotation = rotation
        if scale:
            agent.transform.scale = scale
        
        # Send update to Unity3D
        message = {
            'msg_type': Unity3DProtocol.MSG_AGENT_UPDATE,
            'data': {
                'agent_id': agent_id,
                'transform': {
                    'position': list(agent.transform.position),
                    'rotation': list(agent.transform.rotation),
                    'scale': list(agent.transform.scale)
                },
                'timestamp': time.time()
            }
        }
        self.outgoing_messages.append(message)
    
    def get_status(self) -> Dict[str, Any]:
        """Get adapter status"""
        return {
            "running": self.running,
            "port": self.port,
            "active_connections": len(self.client_connections),
            "embodied_agents": len(self.embodied_agents),
            "pending_actions": len(self.pending_actions),
            "environment_state": self.unity_environment_state,
            "timestamp": time.time()
        }


def main():
    """Test Unity3D integration adapter"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Unity3D Integration Adapter")
    parser.add_argument("--port", type=int, default=7777, help="Port to bind to")
    parser.add_argument("--max-agents", type=int, default=100, help="Maximum number of agents")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    adapter = Unity3DIntegrationAdapter(port=args.port, max_agents=args.max_agents)
    
    try:
        adapter.start_server()
        
        print(f"Unity3D Integration Adapter running on port {args.port}")
        print("Press Ctrl+C to stop...")
        
        while True:
            time.sleep(1)
            
            # Print status every 10 seconds
            if int(time.time()) % 10 == 0:
                status = adapter.get_status()
                print(f"Status: {status['active_connections']} connections, "
                      f"{status['embodied_agents']} agents")
    
    except KeyboardInterrupt:
        print("\nShutting down...")
        adapter.stop_server()
    except Exception as e:
        print(f"Error: {str(e)}")
        adapter.stop_server()


if __name__ == "__main__":
    main()