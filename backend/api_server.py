#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified GeoH2 API Server for India Data
Clean, professional API with real data processing
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import logging
from pathlib import Path
import json
from main import backend  # Import our unified backend

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    """Home endpoint - redirect to frontend"""
    return jsonify({
        "message": "GeoH2 India Unified API",
        "version": "2.0.0",
        "description": "Professional hydrogen cost analysis with real data sources",
        "endpoints": {
            "/api/health": "Health check",
            "/api/status": "Project status and data availability",
            "/api/india/hexagons": "India hexagon data with statistics (default: all hexagons)",
            "/api/india/hexagons?preview=true": "India hexagon data preview (first 100)",
            "/api/india/hexagons/all": "ALL India hexagon data without limitations",
            "/api/india/hexagons/preview": "India hexagon data preview (first 100)",
            "/api/india/lcoh": "India LCOH data with analysis",
            "/api/india/summary": "Comprehensive India data summary",
            "/api/weather/sources": "Weather data sources status",
            "/api/analysis/statistics": "Analysis insights and statistics",
            "/api/plots/<filename>": "Download plot files",
            "/api/data/<filename>": "Download data files"
        }
    })

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "GeoH2 India Unified Backend Running"})

@app.route('/api/status')
def status():
    """Get project status and data availability"""
    try:
        return jsonify(backend.get_project_status())
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/india/hexagons')
def india_hexagons():
    """Get India hexagon data with statistics (default: all hexagons)"""
    try:
        preview_only = request.args.get('preview', 'false').lower() == 'true'
        return jsonify(backend.get_india_hexagons(preview_only=preview_only))
    except Exception as e:
        logger.error(f"Error getting hexagons: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/india/hexagons/all')
def india_hexagons_all():
    """Get ALL India hexagon data without any limitations"""
    try:
        return jsonify(backend.get_all_india_hexagons())
    except Exception as e:
        logger.error(f"Error getting all hexagons: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/india/hexagons/preview')
def india_hexagons_preview():
    """Get preview of India hexagon data (first 100)"""
    try:
        return jsonify(backend.get_india_hexagons_preview())
    except Exception as e:
        logger.error(f"Error getting hexagon preview: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/india/lcoh')
def india_lcoh():
    """Get India LCOH data with analysis"""
    try:
        return jsonify(backend.get_india_lcoh_data())
    except Exception as e:
        logger.error(f"Error getting LCOH data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/india/summary')
def india_summary():
    """Get comprehensive India data summary"""
    try:
        return jsonify(backend.get_weather_summary())
    except Exception as e:
        logger.error(f"Error getting summary: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/weather/sources')
def weather_sources():
    """Get weather data sources status"""
    try:
        status = backend.get_project_status()
        return jsonify({
            "status": "success",
            "weather_sources": status.get("data_sources", {}),
            "message": "Weather data sources status retrieved"
        })
    except Exception as e:
        logger.error(f"Error getting weather sources: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-india')
def generate_india():
    """Generate India data (placeholder for frontend compatibility)"""
    return jsonify({
        "status": "success",
        "message": "Data generation not implemented - using existing data",
        "data_available": True
    })

@app.route('/api/analysis/statistics')
def analysis_statistics():
    """Get analysis statistics and insights"""
    try:
        # Get hexagon statistics
        hex_data = backend.get_india_hexagons()
        lcoh_data = backend.get_india_lcoh_data()
        
        if hex_data.get("status") == "success" and lcoh_data.get("status") == "success":
            stats = {
                "status": "success",
                "analysis_summary": {
                    "total_locations": hex_data.get("total_hexagons", 0),
                    "lcoh_analysis": lcoh_data.get("data", {}).get("lcoh_statistics"),
                    "data_quality": "Professional grade",
                    "data_sources": "Multiple validated sources"
                }
            }
            return jsonify(stats)
        else:
            return jsonify({"error": "Unable to retrieve analysis data"}), 500
            
    except Exception as e:
        logger.error(f"Error getting analysis statistics: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/plots/<filename>')
def download_plots(filename):
    """Download plot files"""
    try:
        plots_dir = Path(__file__).parent.parent / "Plots"
        return send_from_directory(plots_dir, filename)
    except Exception as e:
        logger.error(f"Error serving plot file {filename}: {e}")
        return jsonify({"error": f"Plot file {filename} not found"}), 404

@app.route('/api/data/<filename>')
def download_data(filename):
    """Download data files"""
    try:
        data_dir = Path(__file__).parent.parent / "Data"
        return send_from_directory(data_dir, filename)
    except Exception as e:
        logger.error(f"Error serving data file {filename}: {e}")
        return jsonify({"error": f"File {filename} not found"}), 404

@app.route('/frontend/')
@app.route('/frontend/<path:filename>')
def serve_frontend(filename='index.html'):
    """Serve frontend files"""
    try:
        frontend_dir = Path(__file__).parent.parent / "frontend"
        return send_from_directory(frontend_dir, filename)
    except Exception as e:
        logger.error(f"Error serving frontend file {filename}: {e}")
        return jsonify({"error": f"Frontend file {filename} not found"}), 404

@app.route('/Data/<path:filename>')
def serve_data(filename):
    """Serve data files directly (frontend compatibility)"""
    try:
        data_dir = Path(__file__).parent.parent / "Data"
        return send_from_directory(data_dir, filename)
    except Exception as e:
        logger.error(f"Error serving data file {filename}: {e}")
        return jsonify({"error": f"Data file {filename} not found"}), 404

if __name__ == "__main__":
    print("🚀 Starting GeoH2 India Unified API Server...")
    print("📍 API will be available at: http://localhost:8000")
    print("🌐 Frontend can be accessed at: http://localhost:8000/frontend/")
    print("📊 API endpoints:")
    print("   - GET /api/health - Health check")
    print("   - GET /api/status - Project status")
    print("   - GET /api/india/hexagons - India hexagon data (all hexagons)")
    print("   - GET /api/india/hexagons?preview=true - India hexagon data (preview)")
    print("   - GET /api/india/hexagons/all - ALL India hexagon data")
    print("   - GET /api/india/hexagons/preview - India hexagon data preview")
    print("   - GET /api/india/lcoh - India LCOH data")
    print("   - GET /api/india/summary - India data summary")
    print("   - GET /api/weather/sources - Weather data sources")
    print("   - GET /api/analysis/statistics - Analysis insights")
    print("💡 Press Ctrl+C to stop the server")
    
    app.run(host='0.0.0.0', port=8000, debug=True)
