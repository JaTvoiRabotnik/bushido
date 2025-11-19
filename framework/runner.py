import logging
import vertexai

logger = logging.getLogger(__name__)

def initialize_vertex_ai(project_id: str, location: str) -> bool:
    """Initialize Vertex AI with error handling"""
    if not project_id:
        logger.warning("GOOGLE_CLOUD_PROJECT not set. Set environment variable for production use.")
        logger.warning("Running in test mode without Vertex AI.")
        return False

    try:
        vertexai.init(project=project_id, location=location)
        logger.info(f"Vertex AI initialized: project={project_id}, location={location}")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Vertex AI: {e}")
        logger.warning("Running in test mode without Vertex AI.")
        return False
