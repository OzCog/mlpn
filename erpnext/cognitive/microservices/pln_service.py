"""
PLN (Probabilistic Logic Networks) Inference Microservice

Provides REST API endpoints for probabilistic logic inference operations.
Implements modular PLN inference for deduction, induction, and abduction.
"""

import json
from typing import Dict, List, Any, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cognitive_grammar import PLN, AtomSpace, TruthValue


class PLNHTTPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for PLN inference operations"""
    
    def do_POST(self):
        """Handle POST requests for inference operations"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            
            if path == '/deduction':
                self._handle_deduction(data)
            elif path == '/induction':
                self._handle_induction(data)
            elif path == '/abduction':
                self._handle_abduction(data)
            elif path == '/inference_chain':
                self._handle_inference_chain(data)
            else:
                self._send_error(404, "Endpoint not found")
        except json.JSONDecodeError:
            self._send_error(400, "Invalid JSON")
        except Exception as e:
            self._send_error(500, f"Internal server error: {str(e)}")
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        try:
            if path == '/health':
                self._handle_health_check()
            elif path == '/stats':
                self._handle_get_stats()
            else:
                self._send_error(404, "Endpoint not found")
        except Exception as e:
            self._send_error(500, f"Internal server error: {str(e)}")
    
    def _handle_deduction(self, data):
        """Handle deductive inference request"""
        try:
            premise1_id = data['premise1_id']
            premise2_id = data['premise2_id']
            
            pln = self.server.pln
            result = pln.deduction(premise1_id, premise2_id)
            
            response = {
                "inference_type": "deduction",
                "premise1_id": premise1_id,
                "premise2_id": premise2_id,
                "result": {
                    "strength": result.strength,
                    "confidence": result.confidence
                }
            }
            
            self._send_json_response(response)
        except KeyError as e:
            self._send_error(400, f"Missing required field: {str(e)}")
        except Exception as e:
            self._send_error(500, f"Deduction error: {str(e)}")
    
    def _handle_induction(self, data):
        """Handle inductive inference request"""
        try:
            evidence_links = data['evidence_links']
            
            pln = self.server.pln
            result = pln.induction(evidence_links)
            
            response = {
                "inference_type": "induction",
                "evidence_count": len(evidence_links),
                "evidence_links": evidence_links,
                "result": {
                    "strength": result.strength,
                    "confidence": result.confidence
                }
            }
            
            self._send_json_response(response)
        except KeyError as e:
            self._send_error(400, f"Missing required field: {str(e)}")
        except Exception as e:
            self._send_error(500, f"Induction error: {str(e)}")
    
    def _handle_abduction(self, data):
        """Handle abductive inference request"""
        try:
            observation_id = data['observation_id']
            rule_id = data['rule_id']
            
            pln = self.server.pln
            result = pln.abduction(observation_id, rule_id)
            
            response = {
                "inference_type": "abduction",
                "observation_id": observation_id,
                "rule_id": rule_id,
                "result": {
                    "strength": result.strength,
                    "confidence": result.confidence
                }
            }
            
            self._send_json_response(response)
        except KeyError as e:
            self._send_error(400, f"Missing required field: {str(e)}")
        except Exception as e:
            self._send_error(500, f"Abduction error: {str(e)}")
    
    def _handle_inference_chain(self, data):
        """Handle chained inference operations"""
        try:
            operations = data['operations']
            results = []
            
            pln = self.server.pln
            
            for op in operations:
                op_type = op['type']
                if op_type == 'deduction':
                    result = pln.deduction(op['premise1_id'], op['premise2_id'])
                elif op_type == 'induction':
                    result = pln.induction(op['evidence_links'])
                elif op_type == 'abduction':
                    result = pln.abduction(op['observation_id'], op['rule_id'])
                else:
                    raise ValueError(f"Unknown operation type: {op_type}")
                
                results.append({
                    "operation": op,
                    "result": {
                        "strength": result.strength,
                        "confidence": result.confidence
                    }
                })
            
            response = {
                "inference_type": "chain",
                "operations_count": len(operations),
                "results": results
            }
            
            self._send_json_response(response)
        except KeyError as e:
            self._send_error(400, f"Missing required field: {str(e)}")
        except Exception as e:
            self._send_error(500, f"Inference chain error: {str(e)}")
    
    def _handle_health_check(self):
        """Health check endpoint"""
        self._send_json_response({
            "status": "healthy",
            "service": "pln_inference",
            "version": "1.0.0"
        })
    
    def _handle_get_stats(self):
        """Get PLN service statistics"""
        # Basic stats - in a real implementation, this would track inference operations
        stats = {
            "total_inferences": getattr(self.server, 'inference_count', 0),
            "supported_operations": ["deduction", "induction", "abduction", "inference_chain"],
            "atomspace_size": len(self.server.pln.atomspace.atoms)
        }
        self._send_json_response(stats)
    
    def _send_json_response(self, data, status=200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response_json = json.dumps(data, indent=2)
        self.wfile.write(response_json.encode('utf-8'))
    
    def _send_error(self, status, message):
        """Send error response"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        error_data = {"error": message, "status": status}
        response_json = json.dumps(error_data)
        self.wfile.write(response_json.encode('utf-8'))


class PLNService:
    """
    PLN Inference Microservice
    
    Provides REST API for probabilistic logic inference operations.
    Implements modular PLN inference architecture.
    """
    
    def __init__(self, atomspace: AtomSpace = None, host='localhost', port=8002):
        self.host = host
        self.port = port
        self.atomspace = atomspace or AtomSpace()
        self.pln = PLN(self.atomspace)
        self.server = None
        self.server_thread = None
        self.inference_count = 0
    
    def start(self):
        """Start the PLN inference microservice"""
        self.server = HTTPServer((self.host, self.port), PLNHTTPHandler)
        self.server.pln = self.pln
        self.server.inference_count = self.inference_count
        
        print(f"Starting PLN service on {self.host}:{self.port}")
        
        # Run server in separate thread
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        return self
    
    def stop(self):
        """Stop the PLN inference microservice"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            print("PLN service stopped")
    
    def get_pln(self):
        """Get the underlying PLN instance"""
        return self.pln
    
    def is_running(self):
        """Check if service is running"""
        return self.server is not None and self.server_thread.is_alive()


def main():
    """Run PLN microservice standalone"""
    service = PLNService()
    
    try:
        service.start()
        print("PLN service is running. Press Ctrl+C to stop.")
        
        # Keep main thread alive
        while True:
            pass
            
    except KeyboardInterrupt:
        print("\nShutting down...")
        service.stop()


if __name__ == "__main__":
    main()