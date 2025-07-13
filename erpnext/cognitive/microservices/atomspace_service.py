"""
AtomSpace Microservice

Provides REST API endpoints for hypergraph AtomSpace operations.
Implements modular architecture for cognitive primitive operations.
"""

import json
import uuid
from typing import Dict, List, Any, Optional
from dataclasses import asdict
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cognitive_grammar import AtomSpace, AtomType, LinkType, TruthValue, Atom, Link


class AtomSpaceHTTPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for AtomSpace operations"""
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)
        
        try:
            if path == '/atoms':
                self._handle_list_atoms(query_params)
            elif path == '/links':
                self._handle_list_links(query_params)
            elif path.startswith('/atoms/'):
                atom_id = path.split('/')[-1]
                self._handle_get_atom(atom_id)
            elif path.startswith('/links/'):
                link_id = path.split('/')[-1]
                self._handle_get_link(link_id)
            elif path == '/stats':
                self._handle_get_stats()
            elif path == '/health':
                self._handle_health_check()
            else:
                self._send_error(404, "Endpoint not found")
        except Exception as e:
            self._send_error(500, f"Internal server error: {str(e)}")
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            
            if path == '/atoms':
                self._handle_create_atom(data)
            elif path == '/links':
                self._handle_create_link(data)
            elif path == '/query':
                self._handle_query_atoms(data)
            else:
                self._send_error(404, "Endpoint not found")
        except json.JSONDecodeError:
            self._send_error(400, "Invalid JSON")
        except Exception as e:
            self._send_error(500, f"Internal server error: {str(e)}")
    
    def _handle_list_atoms(self, query_params):
        """List atoms with optional type filtering"""
        atomspace = self.server.atomspace
        atom_type = query_params.get('type', [None])[0]
        
        if atom_type:
            try:
                filter_type = AtomType(atom_type)
                atoms = atomspace.find_atoms_by_type(filter_type)
            except ValueError:
                self._send_error(400, f"Invalid atom type: {atom_type}")
                return
        else:
            atoms = list(atomspace.atoms.values())
        
        response_data = [self._atom_to_dict(atom) for atom in atoms]
        self._send_json_response(response_data)
    
    def _handle_create_atom(self, data):
        """Create new atom"""
        atomspace = self.server.atomspace
        
        try:
            name = data['name']
            atom_type = AtomType(data['type'])
            truth_value = None
            
            if 'truth_value' in data:
                tv_data = data['truth_value']
                truth_value = TruthValue(tv_data['strength'], tv_data['confidence'])
            
            atom_id = atomspace.add_atom(name, atom_type, truth_value)
            atom = atomspace.get_atom(atom_id)
            
            self._send_json_response(self._atom_to_dict(atom), status=201)
        except KeyError as e:
            self._send_error(400, f"Missing required field: {str(e)}")
        except ValueError as e:
            self._send_error(400, f"Invalid value: {str(e)}")
    
    def _handle_get_atom(self, atom_id):
        """Get individual atom by ID"""
        atomspace = self.server.atomspace
        
        try:
            atom = atomspace.get_atom(atom_id)
            if atom:
                self._send_json_response(self._atom_to_dict(atom))
            else:
                self._send_error(404, f"Atom not found: {atom_id}")
        except Exception as e:
            self._send_error(500, f"Error retrieving atom: {str(e)}")
    
    def _handle_list_links(self, query_params):
        """List links with optional type filtering"""
        atomspace = self.server.atomspace
        link_type = query_params.get('type', [None])[0]
        
        if link_type:
            try:
                filter_type = LinkType(link_type)
                links = atomspace.find_links_by_type(filter_type)
            except ValueError:
                self._send_error(400, f"Invalid link type: {link_type}")
                return
        else:
            links = list(atomspace.links.values())
        
        response_data = [self._link_to_dict(link) for link in links]
        self._send_json_response(response_data)
    
    def _handle_create_link(self, data):
        """Create new link"""
        atomspace = self.server.atomspace
        
        try:
            link_type = LinkType(data['type'])
            atoms = data['atoms']
            truth_value = None
            
            if 'truth_value' in data:
                tv_data = data['truth_value']
                truth_value = TruthValue(tv_data['strength'], tv_data['confidence'])
            
            link_id = atomspace.add_link(link_type, atoms, truth_value)
            link = atomspace.get_link(link_id)
            
            self._send_json_response(self._link_to_dict(link), status=201)
        except KeyError as e:
            self._send_error(400, f"Missing required field: {str(e)}")
        except ValueError as e:
            self._send_error(400, f"Invalid value: {str(e)}")
    
    def _handle_get_link(self, link_id):
        """Get individual link by ID"""
        atomspace = self.server.atomspace
        
        try:
            link = atomspace.get_link(link_id)
            if link:
                self._send_json_response(self._link_to_dict(link))
            else:
                self._send_error(404, f"Link not found: {link_id}")
        except Exception as e:
            self._send_error(500, f"Error retrieving link: {str(e)}")
    
    def _handle_query_atoms(self, data):
        """Query atoms based on criteria"""
        atomspace = self.server.atomspace
        
        try:
            # Simple query implementation
            criteria = data.get('criteria', {})
            atom_type = criteria.get('type')
            min_strength = criteria.get('min_strength', 0.0)
            
            atoms = list(atomspace.atoms.values())
            
            if atom_type:
                atoms = [atom for atom in atoms if atom.atom_type.value == atom_type]
            
            if min_strength > 0:
                atoms = [atom for atom in atoms if atom.truth_value.strength >= min_strength]
            
            response_data = [self._atom_to_dict(atom) for atom in atoms]
            self._send_json_response(response_data)
        except Exception as e:
            self._send_error(500, f"Error querying atoms: {str(e)}")
    
    def _handle_get_stats(self):
        """Get AtomSpace statistics"""
        atomspace = self.server.atomspace
        stats = {
            "total_atoms": len(atomspace.atoms),
            "total_links": len(atomspace.links),
            "hypergraph_density": atomspace.get_hypergraph_density(),
        }
        self._send_json_response(stats)
    
    def _handle_health_check(self):
        """Health check endpoint"""
        self._send_json_response({
            "status": "healthy",
            "service": "atomspace",
            "version": "1.0.0"
        })
    
    def _atom_to_dict(self, atom):
        """Convert atom to dictionary"""
        return {
            "id": atom.id,
            "name": atom.name,
            "type": atom.atom_type.value,
            "truth_value": {
                "strength": atom.truth_value.strength,
                "confidence": atom.truth_value.confidence
            },
            "prime_index": atom.prime_index
        }
    
    def _link_to_dict(self, link):
        """Convert link to dictionary"""
        return {
            "id": link.id,
            "type": link.link_type.value,
            "atoms": link.atoms,
            "truth_value": {
                "strength": link.truth_value.strength,
                "confidence": link.truth_value.confidence
            }
        }
    
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


class AtomSpaceService:
    """
    AtomSpace Microservice
    
    Provides REST API for hypergraph AtomSpace operations.
    Implements modular cognitive primitive architecture.
    """
    
    def __init__(self, host='localhost', port=8001):
        self.host = host
        self.port = port
        self.atomspace = AtomSpace()
        self.server = None
        self.server_thread = None
    
    def start(self):
        """Start the AtomSpace microservice"""
        self.server = HTTPServer((self.host, self.port), AtomSpaceHTTPHandler)
        self.server.atomspace = self.atomspace
        
        print(f"Starting AtomSpace service on {self.host}:{self.port}")
        
        # Run server in separate thread
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        return self
    
    def stop(self):
        """Stop the AtomSpace microservice"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            print("AtomSpace service stopped")
    
    def get_atomspace(self):
        """Get the underlying AtomSpace instance"""
        return self.atomspace
    
    def is_running(self):
        """Check if service is running"""
        return self.server is not None and self.server_thread.is_alive()


def main():
    """Run AtomSpace microservice standalone"""
    service = AtomSpaceService()
    
    try:
        service.start()
        print("AtomSpace service is running. Press Ctrl+C to stop.")
        
        # Keep main thread alive
        while True:
            pass
            
    except KeyboardInterrupt:
        print("\nShutting down...")
        service.stop()


if __name__ == "__main__":
    main()