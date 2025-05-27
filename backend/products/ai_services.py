"""
AI services for product recommendations
"""

import logging
from django.conf import settings
import json
import os
import traceback
import openai  # Import the openai module directly for 0.28.0 version

logger = logging.getLogger(__name__)


def get_ai_product_recommendations(user_salary, user_money, period, product_data):
    """
    Get AI-driven financial product recommendations using OpenAI

    Args:
        user_salary (int): User's monthly salary (원)
        user_money (int): User's current possession (원)
        period (int): Desired investment/loan period in months
        product_data (list): List of financial product data for consideration

    Returns:
        dict: AI recommendations with reasoning
    """
    try:
        # Get API key from settings or environment variable
        api_key = getattr(
            settings, "OPENAI_API_KEY", os.environ.get("OPENAI_API_KEY", "")
        )

        if not api_key:
            logger.error("OpenAI API key is not set")
            return {
                "status": "error",
                "message": "OpenAI API key is not configured. Please set the OPENAI_API_KEY.",
            }

        # Set API key for OpenAI 0.28.0
        openai.api_key = api_key

        # Format product data for the prompt
        product_data_str = json.dumps(product_data, ensure_ascii=False, indent=2)

        # Generate prompt for OpenAI
        prompt = f"""
당신은 금융 전문가이며, 사용자의 상황에 맞는 금융 상품을 추천해주는 AI입니다.

사용자 정보:
- 월 소득: {user_salary}원
- 현재 자산: {user_money}원
- 원하는 기간(개월 수): {period}개월

금융 상품 데이터:
{product_data_str}

상품 종류는 예금, 적금, 대출이 있습니다.

추천 조건:
1. 사용자의 연봉과 자산 정보가 있을 경우:
    - 해당 조건과 비슷한 재무 상황을 가진 사람이 선호할 만한 상품을 추천하세요.
    - 기간에 맞는 상품 중 이자율이 높은 예·적금, 낮은 금리의 대출 상품을 우선 추천합니다.
    - 또한 사용자의 자산을 이용하여 예·적금 상품 가입 시 얻을 수 있는 금액을 환산하여 주세요.

2. 사용자의 연봉 및 자산 정보가 없는 경우:
    - 예금/적금은 가장 높은 금리,
    - 대출은 가장 낮은 금리 기준으로 추천하세요.

출력 형식은 다음과 같이 해주세요:
- [상품명] (상품유형) - 금리: X.X%, 기간: X개월
- 추천 사유: [간단한 이유]
- (환산 금액: X.X원)
"""

        try:
            # Call OpenAI API with GPT-4o model using OpenAI 0.28.0 API format
            response = openai.ChatCompletion.create(
                model="gpt-4o",  # Using GPT-4o model for advanced financial analysis
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 재무설계에 전문적인 금융 조언가입니다.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1500,
                temperature=0.7,
            )

            # Extract content from response - OpenAI 0.28.0 format
            recommendation_text = response.choices[0].message["content"]

            # Return the AI-generated recommendations
            return {"status": "success", "recommendations": recommendation_text}

        except Exception as api_error:
            logger.error(f"Error calling OpenAI API: {str(api_error)}")
            error_details = traceback.format_exc()
            logger.error(f"API error details: {error_details}")

            # Try fallback to simpler model
            try:
                logger.info("Trying fallback to text-davinci-003 model")
                response = openai.Completion.create(
                    model="text-davinci-003",
                    prompt=f"당신은 재무설계에 전문적인 금융 조언가입니다.\n\n{prompt}",
                    max_tokens=1500,
                    temperature=0.7,
                )
                recommendation_text = response.choices[0].text.strip()
                return {"status": "success", "recommendations": recommendation_text}
            except Exception as fallback_error:
                return {
                    "status": "error",
                    "message": f"Error calling OpenAI API (both main and fallback): {str(api_error)}",
                }

    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"Error getting AI recommendations: {str(e)}\n{error_details}")
        return {"status": "error", "message": f"AI recommendation failed: {str(e)}"}
