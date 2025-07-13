#!/usr/bin/env python3
"""
Web Agent Integration Adapter

Provides web-based integration for the distributed cognitive mesh.
Handles bidirectional communication with browser-based cognitive agents
and web applications for distributed embodied cognition.

Key Features:
- WebSocket communication with browser agents
- REST API for web applications
- JavaScript SDK compatibility
- Real-time cognitive state synchronization
- Browser-based visualization support
- Cross-origin resource sharing (CORS)
"""

import json
import time
import threading
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
import logging
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, request, jsonify, render_template_string
from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
import uuid

logger = logging.getLogger(__name__)


@dataclass
class WebAgent:
    """Represents a web-based cognitive agent"""
    agent_id: str
    session_id: str
    agent_type: str  # "browser", "node", "service_worker", etc.
    user_agent: str
    capabilities: List[str]
    cognitive_state: Dict[str, Any]
    browser_info: Dict[str, Any]
    last_activity: float = 0.0
    connected: bool = True

    def __post_init__(self):
        if self.last_activity == 0.0:
            self.last_activity = time.time()


@dataclass
class WebTask:
    """Represents a task for web agents"""
    task_id: str
    agent_id: str
    task_type: str
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    status: str = "pending"
    created_at: float = 0.0
    completed_at: Optional[float] = None

    def __post_init__(self):
        if self.created_at == 0.0:
            self.created_at = time.time()


@dataclass
class WebVisualization:
    """Represents a cognitive state visualization for web"""
    viz_id: str
    viz_type: str  # "graph", "heatmap", "timeline", "network", etc.
    data: Dict[str, Any]
    layout: Dict[str, Any]
    interactive: bool = True
    real_time: bool = False

    def __post_init__(self):
        if not hasattr(self, 'layout') or not self.layout:
            self.layout = {"width": 800, "height": 600}


class WebAgentIntegrationAdapter:
    """Main adapter for web agent embodiment integration"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 6666):
        self.host = host
        self.port = port
        
        # Initialize Flask app with SocketIO
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'web-cognitive-mesh-secret'
        self.socketio = SocketIO(
            self.app, 
            cors_allowed_origins="*",
            logger=False,
            engineio_logger=False
        )
        
        # Agent management
        self.web_agents: Dict[str, WebAgent] = {}
        self.active_tasks: Dict[str, WebTask] = {}
        self.visualizations: Dict[str, WebVisualization] = {}
        
        # Session management
        self.session_agents: Dict[str, str] = {}  # session_id -> agent_id
        
        # Real-time data
        self.cognitive_mesh_state = {
            "nodes": [],
            "edges": [],
            "attention_flow": {},
            "processing_load": {}
        }
        
        self.executor = ThreadPoolExecutor(max_workers=50)
        self.running = False
        
        self._setup_routes()
        self._setup_websocket_handlers()
        
        logger.info("Web Agent Integration Adapter initialized")
    
    def _setup_routes(self):
        """Setup REST API routes for web integration"""
        
        @self.app.route('/')
        def dashboard():
            """Main dashboard for cognitive mesh visualization"""
            dashboard_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Cognitive Mesh Dashboard</title>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <script src="https://cdn.socket.io/4.5.0/socket.io.min.js"></script>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
                <style>
                    body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
                    .container { max-width: 1200px; margin: 0 auto; }
                    .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
                    .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 20px; }
                    .metric-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                    .metric-value { font-size: 2em; font-weight: bold; color: #3498db; }
                    .metric-label { color: #7f8c8d; margin-top: 5px; }
                    .visualization { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                    .status-indicator { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 8px; }
                    .status-active { background: #2ecc71; }
                    .status-inactive { background: #e74c3c; }
                    .agent-list { max-height: 400px; overflow-y: auto; }
                    .agent-item { padding: 10px; border-bottom: 1px solid #ecf0f1; }
                    .log-output { background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 8px; height: 300px; overflow-y: auto; font-family: monospace; font-size: 12px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🧠 Distributed Cognitive Mesh Dashboard</h1>
                        <p>Phase 4: Real-time Web Agent Integration & Monitoring</p>
                    </div>
                    
                    <div class="metrics">
                        <div class="metric-card">
                            <div class="metric-value" id="agent-count">0</div>
                            <div class="metric-label">Active Web Agents</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value" id="task-count">0</div>
                            <div class="metric-label">Active Tasks</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value" id="operations-rate">0</div>
                            <div class="metric-label">Operations/Second</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value" id="network-latency">0ms</div>
                            <div class="metric-label">Network Latency</div>
                        </div>
                    </div>
                    
                    <div class="visualization">
                        <h3>Active Web Agents</h3>
                        <div id="agent-list" class="agent-list"></div>
                    </div>
                    
                    <div class="visualization">
                        <h3>Cognitive Network Visualization</h3>
                        <svg id="network-viz" width="100%" height="400"></svg>
                    </div>
                    
                    <div class="visualization">
                        <h3>Real-time Activity Log</h3>
                        <div id="activity-log" class="log-output"></div>
                    </div>
                </div>
                
                <script>
                    // Initialize SocketIO connection
                    const socket = io();
                    
                    // Log function
                    function log(message) {
                        const logElement = document.getElementById('activity-log');
                        const timestamp = new Date().toLocaleTimeString();
                        logElement.innerHTML += `[${timestamp}] ${message}\\n`;
                        logElement.scrollTop = logElement.scrollHeight;
                    }
                    
                    // Update metrics
                    function updateMetrics(data) {
                        document.getElementById('agent-count').textContent = data.agent_count || 0;
                        document.getElementById('task-count').textContent = data.task_count || 0;
                        document.getElementById('operations-rate').textContent = (data.operations_rate || 0).toFixed(1);
                        document.getElementById('network-latency').textContent = `${(data.network_latency || 0).toFixed(1)}ms`;
                    }
                    
                    // Update agent list
                    function updateAgentList(agents) {
                        const agentList = document.getElementById('agent-list');
                        agentList.innerHTML = '';
                        
                        agents.forEach(agent => {
                            const agentItem = document.createElement('div');
                            agentItem.className = 'agent-item';
                            agentItem.innerHTML = `
                                <span class="status-indicator ${agent.connected ? 'status-active' : 'status-inactive'}"></span>
                                <strong>${agent.agent_id}</strong> (${agent.agent_type})
                                <br><small>Capabilities: ${agent.capabilities.join(', ')}</small>
                            `;
                            agentList.appendChild(agentItem);
                        });
                    }
                    
                    // Socket event handlers
                    socket.on('connect', function() {
                        log('Connected to Cognitive Mesh');
                        socket.emit('dashboard_subscribe');
                    });
                    
                    socket.on('dashboard_update', function(data) {
                        updateMetrics(data.metrics);
                        updateAgentList(data.agents);
                        log(`Dashboard updated: ${data.agents.length} agents active`);
                    });
                    
                    socket.on('agent_connected', function(data) {
                        log(`New agent connected: ${data.agent_id} (${data.agent_type})`);
                    });
                    
                    socket.on('agent_disconnected', function(data) {
                        log(`Agent disconnected: ${data.agent_id}`);
                    });
                    
                    socket.on('task_completed', function(data) {
                        log(`Task completed: ${data.task_id} (${data.task_type})`);
                    });
                    
                    socket.on('cognitive_update', function(data) {
                        log(`Cognitive state updated for agent: ${data.agent_id}`);
                    });
                    
                    // Initialize D3.js network visualization
                    const svg = d3.select('#network-viz');
                    const width = 800;
                    const height = 400;
                    
                    const simulation = d3.forceSimulation()
                        .force('link', d3.forceLink().id(d => d.id))
                        .force('charge', d3.forceManyBody().strength(-300))
                        .force('center', d3.forceCenter(width / 2, height / 2));
                    
                    function updateNetworkVisualization(nodes, links) {
                        // Update network visualization with D3.js
                        const link = svg.selectAll('.link')
                            .data(links)
                            .enter().append('line')
                            .attr('class', 'link')
                            .style('stroke', '#999')
                            .style('stroke-opacity', 0.6);
                        
                        const node = svg.selectAll('.node')
                            .data(nodes)
                            .enter().append('circle')
                            .attr('class', 'node')
                            .attr('r', 8)
                            .style('fill', '#3498db');
                        
                        simulation.nodes(nodes).on('tick', () => {
                            link.attr('x1', d => d.source.x)
                                .attr('y1', d => d.source.y)
                                .attr('x2', d => d.target.x)
                                .attr('y2', d => d.target.y);
                            
                            node.attr('cx', d => d.x)
                                .attr('cy', d => d.y);
                        });
                        
                        simulation.force('link').links(links);
                        simulation.alpha(1).restart();
                    }
                    
                    log('Dashboard initialized');
                </script>
            </body>
            </html>
            """
            return dashboard_html
        
        @self.app.route('/api/agents', methods=['GET'])
        def list_web_agents():
            """List all active web agents"""
            agents = [asdict(agent) for agent in self.web_agents.values()]
            return jsonify({
                "agents": agents,
                "count": len(agents),
                "timestamp": time.time()
            })
        
        @self.app.route('/api/agents/<agent_id>', methods=['GET'])
        def get_web_agent(agent_id):
            """Get specific web agent details"""
            if agent_id not in self.web_agents:
                return jsonify({"error": "Agent not found"}), 404
            
            agent = self.web_agents[agent_id]
            return jsonify({
                "agent": asdict(agent),
                "timestamp": time.time()
            })
        
        @self.app.route('/api/tasks', methods=['POST'])
        def create_web_task():
            """Create a new task for web agents"""
            try:
                data = request.get_json()
                task = WebTask(
                    task_id=str(uuid.uuid4()),
                    agent_id=data.get('agent_id'),
                    task_type=data.get('task_type', 'generic'),
                    input_data=data.get('input_data', {})
                )
                
                self.active_tasks[task.task_id] = task
                
                # Assign task to agent
                self._assign_web_task(task)
                
                return jsonify({
                    "status": "created",
                    "task": asdict(task)
                })
                
            except Exception as e:
                logger.error(f"Web task creation error: {str(e)}")
                return jsonify({"error": "An internal error has occurred."}), 500
        
        @self.app.route('/api/tasks/<task_id>', methods=['GET'])
        def get_web_task(task_id):
            """Get task status and results"""
            if task_id not in self.active_tasks:
                return jsonify({"error": "Task not found"}), 404
            
            task = self.active_tasks[task_id]
            return jsonify({
                "task": asdict(task),
                "timestamp": time.time()
            })
        
        @self.app.route('/api/cognitive/synthesize', methods=['POST'])
        def web_cognitive_synthesize():
            """Cognitive synthesis endpoint for web agents"""
            try:
                data = request.get_json()
                
                # Simulate cognitive synthesis
                symbolic_input = data.get('symbolic_input', {})
                neural_input = data.get('neural_input', [])
                
                # Simple synthesis simulation
                result = np.random.randn(128).tolist()
                
                return jsonify({
                    "status": "success",
                    "result": result,
                    "synthesis_type": data.get('synthesis_type', 'conceptual_embedding'),
                    "timestamp": time.time()
                })
                
            except Exception as e:
                logger.error(f"Web synthesis error: {str(e)}")
                return jsonify({"error": "An internal error has occurred."}), 500
        
        @self.app.route('/api/visualizations', methods=['GET'])
        def list_visualizations():
            """List available cognitive visualizations"""
            vizs = [asdict(viz) for viz in self.visualizations.values()]
            return jsonify({
                "visualizations": vizs,
                "count": len(vizs),
                "timestamp": time.time()
            })
        
        @self.app.route('/api/visualizations', methods=['POST'])
        def create_visualization():
            """Create a new cognitive visualization"""
            try:
                data = request.get_json()
                viz = WebVisualization(
                    viz_id=str(uuid.uuid4()),
                    viz_type=data.get('viz_type', 'graph'),
                    data=data.get('data', {}),
                    layout=data.get('layout', {}),
                    interactive=data.get('interactive', True),
                    real_time=data.get('real_time', False)
                )
                
                self.visualizations[viz.viz_id] = viz
                
                return jsonify({
                    "status": "created",
                    "visualization": asdict(viz)
                })
                
            except Exception as e:
                logger.error(f"Visualization creation error: {str(e)}")
                return jsonify({"error": "An internal error has occurred."}), 500
        
        @self.app.route('/api/mesh/state', methods=['GET'])
        def get_mesh_state():
            """Get current cognitive mesh state"""
            return jsonify({
                "mesh_state": self.cognitive_mesh_state,
                "active_agents": len(self.web_agents),
                "active_tasks": len(self.active_tasks),
                "timestamp": time.time()
            })
        
        @self.app.route('/sdk/cognitive-agent.js', methods=['GET'])
        def cognitive_agent_sdk():
            """Serve JavaScript SDK for web agents"""
            sdk_js = """
            /**
             * Cognitive Agent SDK for Web Integration
             * Provides JavaScript interface for browser-based cognitive agents
             */
            
            class CognitiveAgent {
                constructor(agentType = 'browser', capabilities = []) {
                    this.agentId = this.generateAgentId();
                    this.agentType = agentType;
                    this.capabilities = capabilities;
                    this.cognitiveState = {};
                    this.connected = false;
                    this.socket = null;
                    
                    this.init();
                }
                
                generateAgentId() {
                    return 'web_agent_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
                }
                
                init() {
                    // Initialize SocketIO connection
                    this.socket = io();
                    
                    this.socket.on('connect', () => {
                        this.connected = true;
                        this.register();
                        console.log('Cognitive Agent connected:', this.agentId);
                    });
                    
                    this.socket.on('disconnect', () => {
                        this.connected = false;
                        console.log('Cognitive Agent disconnected');
                    });
                    
                    this.socket.on('task_assignment', (data) => {
                        this.handleTaskAssignment(data);
                    });
                    
                    this.socket.on('cognitive_update', (data) => {
                        this.handleCognitiveUpdate(data);
                    });
                }
                
                register() {
                    const registrationData = {
                        agent_id: this.agentId,
                        agent_type: this.agentType,
                        capabilities: this.capabilities,
                        browser_info: {
                            user_agent: navigator.userAgent,
                            platform: navigator.platform,
                            language: navigator.language,
                            screen: {
                                width: screen.width,
                                height: screen.height
                            }
                        }
                    };
                    
                    this.socket.emit('register_agent', registrationData);
                }
                
                updateCognitiveState(state) {
                    this.cognitiveState = { ...this.cognitiveState, ...state };
                    
                    if (this.connected) {
                        this.socket.emit('cognitive_state_update', {
                            agent_id: this.agentId,
                            cognitive_state: this.cognitiveState
                        });
                    }
                }
                
                synthesize(symbolicInput, neuralInput, synthesisType = 'conceptual_embedding') {
                    return new Promise((resolve, reject) => {
                        fetch('/api/cognitive/synthesize', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({
                                symbolic_input: symbolicInput,
                                neural_input: neuralInput,
                                synthesis_type: synthesisType
                            })
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.status === 'success') {
                                resolve(data.result);
                            } else {
                                reject(new Error(data.error || 'Synthesis failed'));
                            }
                        })
                        .catch(error => reject(error));
                    });
                }
                
                createTask(taskType, inputData) {
                    return new Promise((resolve, reject) => {
                        fetch('/api/tasks', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({
                                agent_id: this.agentId,
                                task_type: taskType,
                                input_data: inputData
                            })
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.status === 'created') {
                                resolve(data.task);
                            } else {
                                reject(new Error(data.error || 'Task creation failed'));
                            }
                        })
                        .catch(error => reject(error));
                    });
                }
                
                handleTaskAssignment(data) {
                    console.log('Task assigned:', data);
                    // Override this method to handle task assignments
                }
                
                handleCognitiveUpdate(data) {
                    console.log('Cognitive update received:', data);
                    // Override this method to handle cognitive updates
                }
                
                sendEvent(eventType, eventData) {
                    if (this.connected) {
                        this.socket.emit('agent_event', {
                            agent_id: this.agentId,
                            event_type: eventType,
                            event_data: eventData,
                            timestamp: Date.now()
                        });
                    }
                }
                
                disconnect() {
                    if (this.socket) {
                        this.socket.disconnect();
                    }
                }
            }
            
            // Make CognitiveAgent available globally
            window.CognitiveAgent = CognitiveAgent;
            """
            
            from flask import Response
            return Response(sdk_js, mimetype='application/javascript')
    
    def _setup_websocket_handlers(self):
        """Setup WebSocket event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            session_id = request.sid
            logger.info(f"Web client connected: {session_id}")
            
            emit('connected', {
                "status": "connected",
                "session_id": session_id,
                "server_info": {
                    "capabilities": [
                        "real_time_synthesis",
                        "task_assignment",
                        "cognitive_visualization",
                        "browser_integration"
                    ]
                },
                "timestamp": time.time()
            })
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            session_id = request.sid
            
            # Find and remove agent
            if session_id in self.session_agents:
                agent_id = self.session_agents[session_id]
                if agent_id in self.web_agents:
                    self.web_agents[agent_id].connected = False
                    emit('agent_disconnected', {
                        "agent_id": agent_id,
                        "timestamp": time.time()
                    }, broadcast=True)
                
                del self.session_agents[session_id]
            
            logger.info(f"Web client disconnected: {session_id}")
        
        @self.socketio.on('register_agent')
        def handle_register_agent(data):
            """Register a new web agent"""
            session_id = request.sid
            agent_id = data.get('agent_id')
            
            if not agent_id:
                agent_id = f"web_agent_{session_id}_{int(time.time())}"
            
            agent = WebAgent(
                agent_id=agent_id,
                session_id=session_id,
                agent_type=data.get('agent_type', 'browser'),
                user_agent=data.get('browser_info', {}).get('user_agent', ''),
                capabilities=data.get('capabilities', []),
                cognitive_state={},
                browser_info=data.get('browser_info', {})
            )
            
            self.web_agents[agent_id] = agent
            self.session_agents[session_id] = agent_id
            
            logger.info(f"Web agent registered: {agent_id}")
            
            emit('agent_registered', {
                "agent_id": agent_id,
                "status": "registered",
                "timestamp": time.time()
            })
            
            # Broadcast to dashboard
            emit('agent_connected', {
                "agent_id": agent_id,
                "agent_type": agent.agent_type,
                "capabilities": agent.capabilities,
                "timestamp": time.time()
            }, broadcast=True)
        
        @self.socketio.on('cognitive_state_update')
        def handle_cognitive_state_update(data):
            """Handle cognitive state update from web agent"""
            agent_id = data.get('agent_id')
            cognitive_state = data.get('cognitive_state', {})
            
            if agent_id in self.web_agents:
                agent = self.web_agents[agent_id]
                agent.cognitive_state.update(cognitive_state)
                agent.last_activity = time.time()
                
                # Broadcast cognitive update
                emit('cognitive_update', {
                    "agent_id": agent_id,
                    "cognitive_state": cognitive_state,
                    "timestamp": time.time()
                }, broadcast=True)
        
        @self.socketio.on('task_result')
        def handle_task_result(data):
            """Handle task result from web agent"""
            task_id = data.get('task_id')
            result = data.get('result', {})
            status = data.get('status', 'completed')
            
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]
                task.output_data = result
                task.status = status
                task.completed_at = time.time()
                
                # Broadcast task completion
                emit('task_completed', {
                    "task_id": task_id,
                    "result": result,
                    "status": status,
                    "task_type": task.task_type,
                    "timestamp": time.time()
                }, broadcast=True)
                
                logger.info(f"Web task completed: {task_id}")
        
        @self.socketio.on('agent_event')
        def handle_agent_event(data):
            """Handle custom events from web agents"""
            agent_id = data.get('agent_id')
            event_type = data.get('event_type')
            event_data = data.get('event_data', {})
            
            logger.info(f"Agent event: {agent_id} - {event_type}")
            
            # Process specific event types
            if event_type == 'attention_focus':
                self._handle_attention_focus(agent_id, event_data)
            elif event_type == 'cognitive_synthesis':
                self._handle_cognitive_synthesis_request(agent_id, event_data)
            elif event_type == 'visualization_request':
                self._handle_visualization_request(agent_id, event_data)
        
        @self.socketio.on('dashboard_subscribe')
        def handle_dashboard_subscribe():
            """Subscribe to dashboard updates"""
            join_room('dashboard')
            
            # Send initial dashboard data
            emit('dashboard_update', {
                "metrics": {
                    "agent_count": len(self.web_agents),
                    "task_count": len(self.active_tasks),
                    "operations_rate": 0.0,  # Would be calculated in real implementation
                    "network_latency": 0.0
                },
                "agents": [asdict(agent) for agent in self.web_agents.values()],
                "timestamp": time.time()
            })
    
    def _assign_web_task(self, task: WebTask):
        """Assign a task to a web agent"""
        if task.agent_id not in self.web_agents:
            logger.warning(f"Cannot assign task to unknown agent: {task.agent_id}")
            return
        
        agent = self.web_agents[task.agent_id]
        if not agent.connected:
            logger.warning(f"Cannot assign task to disconnected agent: {task.agent_id}")
            return
        
        # Send task assignment via WebSocket
        self.socketio.emit('task_assignment', {
            "task": asdict(task),
            "timestamp": time.time()
        }, room=agent.session_id)
        
        task.status = "assigned"
        logger.info(f"Task assigned to web agent: {task.task_id} -> {task.agent_id}")
    
    def _handle_attention_focus(self, agent_id: str, event_data: Dict[str, Any]):
        """Handle attention focus event from web agent"""
        # Update cognitive mesh state with attention information
        self.cognitive_mesh_state["attention_flow"][agent_id] = {
            "focus_target": event_data.get('target'),
            "intensity": event_data.get('intensity', 1.0),
            "timestamp": time.time()
        }
    
    def _handle_cognitive_synthesis_request(self, agent_id: str, event_data: Dict[str, Any]):
        """Handle cognitive synthesis request from web agent"""
        # Process synthesis request and send result back
        result = np.random.randn(128).tolist()  # Placeholder
        
        self.socketio.emit('synthesis_result', {
            "agent_id": agent_id,
            "result": result,
            "synthesis_type": event_data.get('synthesis_type', 'conceptual_embedding'),
            "timestamp": time.time()
        }, room=self.web_agents[agent_id].session_id)
    
    def _handle_visualization_request(self, agent_id: str, event_data: Dict[str, Any]):
        """Handle visualization request from web agent"""
        viz_type = event_data.get('viz_type', 'graph')
        
        # Create visualization data
        viz_data = self._generate_visualization_data(viz_type)
        
        self.socketio.emit('visualization_data', {
            "agent_id": agent_id,
            "visualization": viz_data,
            "timestamp": time.time()
        }, room=self.web_agents[agent_id].session_id)
    
    def _generate_visualization_data(self, viz_type: str) -> Dict[str, Any]:
        """Generate visualization data for web agents"""
        if viz_type == 'network':
            # Generate network graph data
            nodes = [{"id": agent_id, "type": agent.agent_type} 
                    for agent_id, agent in self.web_agents.items()]
            links = []  # Would be populated with actual connections
            
            return {
                "type": "network",
                "nodes": nodes,
                "links": links
            }
        
        elif viz_type == 'attention_heatmap':
            # Generate attention heatmap data
            return {
                "type": "heatmap",
                "data": self.cognitive_mesh_state.get("attention_flow", {}),
                "layout": {"width": 600, "height": 400}
            }
        
        else:
            # Default visualization
            return {
                "type": "graph",
                "data": {"message": f"Visualization type '{viz_type}' not implemented yet"}
            }
    
    def start_server(self):
        """Start the web integration server"""
        self.running = True
        
        # Start background services
        threading.Thread(target=self._monitor_agents, daemon=True).start()
        threading.Thread(target=self._update_dashboard, daemon=True).start()
        
        logger.info(f"Web Agent Integration server starting on {self.host}:{self.port}")
        self.socketio.run(self.app, host=self.host, port=self.port, debug=False)
    
    def stop_server(self):
        """Stop the web integration server"""
        self.running = False
        logger.info("Web Agent Integration server stopped")
    
    def _monitor_agents(self):
        """Monitor agent connectivity and health"""
        while self.running:
            try:
                current_time = time.time()
                expired_agents = []
                
                for agent_id, agent in self.web_agents.items():
                    if current_time - agent.last_activity > 300:  # 5 minutes timeout
                        expired_agents.append(agent_id)
                
                # Remove expired agents
                for agent_id in expired_agents:
                    del self.web_agents[agent_id]
                    logger.info(f"Removed expired web agent: {agent_id}")
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Agent monitoring error: {str(e)}")
    
    def _update_dashboard(self):
        """Update dashboard with real-time data"""
        while self.running:
            try:
                dashboard_data = {
                    "metrics": {
                        "agent_count": len(self.web_agents),
                        "task_count": len(self.active_tasks),
                        "operations_rate": 0.0,  # Would calculate actual rate
                        "network_latency": 0.0
                    },
                    "agents": [asdict(agent) for agent in self.web_agents.values()],
                    "timestamp": time.time()
                }
                
                self.socketio.emit('dashboard_update', dashboard_data, room='dashboard')
                
                time.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                logger.error(f"Dashboard update error: {str(e)}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get adapter status"""
        return {
            "running": self.running,
            "host": self.host,
            "port": self.port,
            "active_agents": len(self.web_agents),
            "active_tasks": len(self.active_tasks),
            "visualizations": len(self.visualizations),
            "cognitive_mesh_state": self.cognitive_mesh_state,
            "timestamp": time.time()
        }


def main():
    """Test web agent integration adapter"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Web Agent Integration Adapter")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=6666, help="Port to bind to")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    adapter = WebAgentIntegrationAdapter(host=args.host, port=args.port)
    
    try:
        print(f"Web Agent Integration Adapter starting on {args.host}:{args.port}")
        print("Open http://localhost:6666 in your browser to access the dashboard")
        print("Press Ctrl+C to stop...")
        
        adapter.start_server()
    
    except KeyboardInterrupt:
        print("\nShutting down...")
        adapter.stop_server()
    except Exception as e:
        print(f"Error: {str(e)}")
        adapter.stop_server()


if __name__ == "__main__":
    main()