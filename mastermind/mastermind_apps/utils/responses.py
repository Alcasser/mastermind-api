# Python
import logging
logger = logging.getLogger(__name__)


def process_response(response_dic, details=None, error=False):
    # Create log if hiddenError
    if details:
        # Fill dict with detail. Ex: {"hiddenError": ["Message {detail}"]}
        response_dic[list(response_dic.keys())[0]] = [
            list(response_dic.values())[0][0].format(*details)]

    if "hiddenError" in response_dic:
        if error:
            logger.error(response_dic)
        else:
            logger.warning(response_dic)
    return response_dic
