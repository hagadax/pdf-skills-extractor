import azure.functions as func
import logging
import json
from datetime import datetime
import sys
import os

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from monthly_analysis import monthly_analyzer
    from keyvault_manager import get_application_config
except ImportError as e:
    logging.error(f"Failed to import modules: {e}")

app = func.FunctionApp()

@app.timer_trigger(schedule="0 0 1 * *", arg_name="mytimer", run_on_startup=False,
                  use_monitor=False) 
def monthly_skills_analysis_timer(mytimer: func.TimerRequest) -> None:
    """
    Azure Function that runs on the 1st day of every month at midnight (UTC)
    to perform automated monthly skills analysis.
    
    Cron schedule: "0 0 1 * *" means:
    - 0 minutes
    - 0 hours (midnight)
    - 1st day of month
    - every month
    - any day of week
    """
    utc_timestamp = datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info(f'Monthly Skills Analysis Timer triggered at {utc_timestamp}')
    
    try:
        # Initialize configuration
        config = get_application_config()
        logging.info("Key Vault configuration loaded successfully")
        
        # Run monthly analysis
        success = monthly_analyzer.schedule_monthly_analysis()
        
        if success:
            logging.info("Monthly skills analysis completed successfully")
            
            # Get the generated report
            latest_report = monthly_analyzer.get_latest_report()
            
            # Log summary statistics
            if latest_report:
                logging.info(f"Analysis Summary:")
                logging.info(f"- Month: {latest_report.get('analysis_month', 'Unknown')}")
                logging.info(f"- Total Documents: {latest_report.get('total_documents', 0)}")
                logging.info(f"- Resumes: {latest_report.get('total_resumes', 0)}")
                logging.info(f"- Job Descriptions: {latest_report.get('total_job_descriptions', 0)}")
                logging.info(f"- Top Technical Skills: {len(latest_report.get('top_technical_skills', []))}")
                logging.info(f"- Top Soft Skills: {len(latest_report.get('top_soft_skills', []))}")
        else:
            logging.error("Monthly skills analysis failed")
            
    except Exception as e:
        logging.error(f"Error during monthly analysis: {str(e)}")
        raise


@app.http_trigger(route="monthly-analysis", auth_level=func.AuthLevel.FUNCTION)
def monthly_analysis_http(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP trigger to manually run monthly analysis or get latest report.
    
    GET: Returns the latest monthly report
    POST: Triggers a new monthly analysis for specified month
    """
    logging.info('Monthly Analysis HTTP trigger function processed a request.')

    try:
        if req.method == 'GET':
            # Return latest report
            latest_report = monthly_analyzer.get_latest_report()
            
            if latest_report:
                return func.HttpResponse(
                    json.dumps(latest_report, indent=2, default=str),
                    status_code=200,
                    mimetype="application/json"
                )
            else:
                return func.HttpResponse(
                    json.dumps({"message": "No monthly reports found"}),
                    status_code=404,
                    mimetype="application/json"
                )
        
        elif req.method == 'POST':
            # Trigger new analysis
            try:
                req_body = req.get_json()
                target_month = req_body.get('month') if req_body else None
                
                # Generate report
                report = monthly_analyzer.generate_monthly_report(target_month)
                
                return func.HttpResponse(
                    json.dumps({
                        "message": "Monthly analysis completed successfully",
                        "analysis_month": report.analysis_month,
                        "total_documents": report.total_documents,
                        "report_generated_at": report.generated_at
                    }, default=str),
                    status_code=200,
                    mimetype="application/json"
                )
                
            except Exception as e:
                logging.error(f"Error generating monthly report: {str(e)}")
                return func.HttpResponse(
                    json.dumps({"error": f"Failed to generate report: {str(e)}"}),
                    status_code=500,
                    mimetype="application/json"
                )
        
        else:
            return func.HttpResponse(
                json.dumps({"error": "Method not allowed"}),
                status_code=405,
                mimetype="application/json"
            )

    except Exception as e:
        logging.error(f"Error in monthly analysis HTTP function: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )


@app.http_trigger(route="analysis-dashboard", auth_level=func.AuthLevel.ANONYMOUS)
def analysis_dashboard(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP trigger to provide a simple dashboard view of the latest analysis.
    """
    try:
        latest_report = monthly_analyzer.get_latest_report()
        
        if not latest_report:
            return func.HttpResponse(
                "<html><body><h1>No Analysis Data Available</h1></body></html>",
                status_code=404,
                mimetype="text/html"
            )
        
        # Generate HTML dashboard
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Monthly Skills Analysis Dashboard</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
                .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }}
                .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #007bff; }}
                .skill-section {{ margin-bottom: 30px; }}
                .skill-list {{ background: #f8f9fa; padding: 15px; border-radius: 8px; }}
                .skill-item {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #e9ecef; }}
                .recommendations {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 8px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Monthly Skills Analysis Dashboard</h1>
                    <p>Analysis for: <strong>{latest_report.get('analysis_month', 'Unknown')}</strong></p>
                    <p>Generated: {latest_report.get('generated_at', 'Unknown')}</p>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>📄 Total Documents</h3>
                        <h2>{latest_report.get('total_documents', 0)}</h2>
                    </div>
                    <div class="stat-card">
                        <h3>👤 Resumes</h3>
                        <h2>{latest_report.get('total_resumes', 0)}</h2>
                    </div>
                    <div class="stat-card">
                        <h3>💼 Job Descriptions</h3>
                        <h2>{latest_report.get('total_job_descriptions', 0)}</h2>
                    </div>
                    <div class="stat-card">
                        <h3>🤖 AI Service</h3>
                        <h2>{latest_report.get('ai_extraction_stats', {}).get('service_type', 'Unknown')}</h2>
                    </div>
                </div>
                
                <div class="skill-section">
                    <h2>🚀 Top Technical Skills</h2>
                    <div class="skill-list">
                        {''.join([f'<div class="skill-item"><span>{skill["skill"]}</span><span>{skill["count"]} mentions ({skill["percentage"]}%)</span></div>' for skill in latest_report.get('top_technical_skills', [])[:10]])}
                    </div>
                </div>
                
                <div class="skill-section">
                    <h2>💫 Top Soft Skills</h2>
                    <div class="skill-list">
                        {''.join([f'<div class="skill-item"><span>{skill["skill"]}</span><span>{skill["count"]} mentions ({skill["percentage"]}%)</span></div>' for skill in latest_report.get('top_soft_skills', [])[:10]])}
                    </div>
                </div>
                
                <div class="skill-section">
                    <h2>⬆️ Emerging Skills</h2>
                    <div class="skill-list">
                        {''.join([f'<div class="skill-item"><span>{skill["skill"]}</span><span>{skill["count"]} mentions ({skill["change"]})</span></div>' for skill in latest_report.get('emerging_skills', [])[:5]])}
                    </div>
                </div>
                
                <div class="recommendations">
                    <h2>💡 Recommendations</h2>
                    <ul>
                        {''.join([f'<li>{rec}</li>' for rec in latest_report.get('recommendations', [])])}
                    </ul>
                </div>
            </div>
        </body>
        </html>
        """
        
        return func.HttpResponse(
            html_content,
            status_code=200,
            mimetype="text/html"
        )
        
    except Exception as e:
        logging.error(f"Error generating dashboard: {str(e)}")
        return func.HttpResponse(
            f"<html><body><h1>Error</h1><p>{str(e)}</p></body></html>",
            status_code=500,
            mimetype="text/html"
        )