"""
Google Trends 애플리케이션 예제 구조

이 파일은 Google Trends 애플리케이션의 권장 구조를 보여주는 예시입니다.
실제 구현 시에는 각 파일을 적절히 분리하여 모듈화된 구조로 개발하는 것이 좋습니다.
"""

from typing import Dict, List, Optional, Union, Any
from datetime import datetime
import logging
from flask import Flask, render_template, jsonify, request
from pytrends.request import TrendReq
import pandas as pd
import time
import os

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Flask 애플리케이션 초기화
app = Flask(__name__)

# 캐시 설정 (간단한 메모리 캐시)
cache = {}
CACHE_TIMEOUT = 3600  # 1시간

# Google Trends API 클래스
class GoogleTrendsAPI:
    """Google Trends API 래퍼 클래스
    
    Google Trends API 요청을 관리하고 데이터를 가져오는 클래스입니다.
    요청 제한 관리, 에러 처리, 데이터 정제 등의 기능을 제공합니다.
    """
    
    def __init__(self, hl: str = 'ko-KR', tz: int = 540, timeout: tuple = (10, 25)):
        """GoogleTrendsAPI 초기화
        
        Args:
            hl: 언어 설정
            tz: 시간대
            timeout: 요청 타임아웃 (연결 타임아웃, 읽기 타임아웃)
        """
        self.hl = hl
        self.tz = tz
        self.timeout = timeout
        self._pytrends = None
    
    @property
    def pytrends(self) -> TrendReq:
        """TrendReq 인스턴스 반환
        
        매번 새로운 인스턴스를 생성하지 않고 필요할 때만 생성하여 반환합니다.
        
        Returns:
            TrendReq: pytrends 인스턴스
        """
        if self._pytrends is None:
            self._pytrends = TrendReq(
                hl=self.hl,
                tz=self.tz,
                timeout=self.timeout
            )
        return self._pytrends
    
    def get_realtime_trends(self) -> List[str]:
        """실시간 인기 검색어를 가져오는 함수
        
        Returns:
            List[str]: 인기 검색어 목록
        """
        logger.info("실시간 인기 검색어 가져오기 시도")
        
        try:
            # 여러 국가 코드 시도
            countries = ['KR', 'US', 'GB', 'JP']
            
            for country in countries:
                try:
                    # 인기 검색어 리스트 - 검색량이 높은 일반적인 키워드
                    popular_keywords = [
                        "코로나", "날씨", "주식", "부동산", "뉴스", 
                        "스포츠", "연예", "게임", "쇼핑", "여행"
                    ]
                    
                    # 요청 간 지연 시간 추가
                    time.sleep(1)
                    
                    # 최근 7일 데이터 요청
                    timeframe = 'now 7-d'
                    self.pytrends.build_payload(
                        kw_list=popular_keywords[:5],
                        timeframe=timeframe,
                        geo=country
                    )
                    
                    # 데이터 가져오기
                    interest_df = self.pytrends.interest_over_time()
                    
                    if not interest_df.empty:
                        logger.info(f"성공: {country}의 interest_over_time 데이터를 가져왔습니다.")
                        
                        # 마지막 데이터 행에서 가장 인기 있는 키워드 순으로 정렬
                        latest_data = interest_df.iloc[-1].sort_values(ascending=False)
                        trends = []
                        
                        # 'isPartial' 열 제외하고 키워드만 추출
                        for keyword in latest_data.index:
                            if keyword != 'isPartial':
                                trends.append(keyword)
                        
                        # 나머지 키워드 추가 (총 10개 맞추기)
                        if len(trends) < 10:
                            for keyword in popular_keywords:
                                if keyword not in trends:
                                    trends.append(keyword)
                                    if len(trends) >= 10:
                                        break
                        
                        return trends[:10]  # 상위 10개 반환
                
                except Exception as e:
                    logger.error(f"{country} 지역 시도 실패: {e}")
                    continue
            
            # 모든 국가 시도 실패 시 대체 키워드 리스트 반환
            logger.warning("모든 국가 시도 실패, 대체 키워드 리스트 반환")
            return ["뉴스", "날씨", "음악", "영화", "주식", "부동산", "게임", "스포츠", "쇼핑", "건강"]
        
        except Exception as e:
            logger.error(f"모든 방법 실패: {e}")
            return ["뉴스", "날씨", "음악", "영화", "주식", "부동산", "게임", "스포츠", "쇼핑", "건강"]
    
    def get_related_queries(self, keyword: str, country: str = 'KR') -> Dict[str, List[Dict[str, Any]]]:
        """특정 키워드에 대한 관련 검색어를 가져오는 함수
        
        Args:
            keyword: 관련 검색어를 찾을 키워드
            country: 국가 코드
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: 관련 검색어 정보 (상위 및 급상승 검색어)
        """
        result = {'top': [], 'rising': []}
        
        try:
            logger.info(f"키워드 '{keyword}'에 대한 관련 검색어 가져오기 시도...")
            
            # 여러 국가 코드 시도
            countries = [country, 'US', 'GB', 'JP']
            
            for curr_country in countries:
                try:
                    # 시간 간격 설정: "today 1-m" (1달) 대신 "today 3-m" (3달)로 변경해서 시도
                    timeframe = 'today 3-m'
                    logger.info(f"  국가 '{curr_country}', 기간 '{timeframe}'으로 시도 중...")
                    
                    # 데이터 요청 설정
                    self.pytrends.build_payload(
                        kw_list=[keyword],
                        timeframe=timeframe,
                        geo=curr_country
                    )
                    
                    # 잠시 대기
                    time.sleep(1)
                    
                    # 관련 검색어 가져오기
                    related_queries = self.pytrends.related_queries()
                    
                    logger.info(f"  관련 검색어 결과: {keyword in related_queries}")
                    
                    if keyword in related_queries and related_queries[keyword]:
                        # 상위 관련 검색어
                        if 'top' in related_queries[keyword] and not related_queries[keyword]['top'].empty:
                            top_df = related_queries[keyword]['top']
                            logger.info(f"  상위 관련 검색어 {len(top_df)}개 발견")
                            
                            try:
                                result['top'] = []
                                for _, row in top_df.iterrows():
                                    try:
                                        result['top'].append({
                                            'query': row['query'] if 'query' in row else "알 수 없음",
                                            'value': int(row['value']) if 'value' in row else 0
                                        })
                                    except Exception as e:
                                        logger.error(f"    행 처리 오류: {e}")
                                        continue
                            except Exception as e:
                                logger.error(f"  상위 관련 검색어 처리 오류: {e}")
                        
                        # 급상승 관련 검색어
                        if 'rising' in related_queries[keyword] and not related_queries[keyword]['rising'].empty:
                            rising_df = related_queries[keyword]['rising']
                            logger.info(f"  급상승 관련 검색어 {len(rising_df)}개 발견")
                            
                            try:
                                result['rising'] = []
                                for _, row in rising_df.iterrows():
                                    try:
                                        result['rising'].append({
                                            'query': row['query'] if 'query' in row else "알 수 없음",
                                            'value': row['value'] if 'value' in row else "Infinity"
                                        })
                                    except Exception as e:
                                        logger.error(f"    행 처리 오류: {e}")
                                        continue
                            except Exception as e:
                                logger.error(f"  급상승 관련 검색어 처리 오류: {e}")
                        
                        # 결과가 있으면 현재 반복 종료
                        if result['top'] or result['rising']:
                            logger.info(f"  성공: '{curr_country}'에서 관련 검색어를 찾았습니다.")
                            return result
                    
                    logger.warning(f"  '{curr_country}'에서 관련 검색어를 찾지 못했습니다.")
                
                except Exception as e:
                    logger.error(f"  '{curr_country}' 시도 중 오류: {e}")
            
            # 관련 검색어를 찾지 못한 경우 대체 데이터 제공
            if keyword in ["날씨", "뉴스", "코로나", "주식", "연예", "게임", "쇼핑", "여행", "부동산", "스포츠"]:
                logger.info("  대체 샘플 데이터 제공")
                return self.get_sample_related_data(keyword)
            
            logger.warning("관련 검색어를 찾지 못했습니다.")
            return result
        
        except Exception as e:
            logger.error(f"관련 검색어 가져오기 전체 실패: {e}")
            return result
    
    def get_sample_related_data(self, keyword: str) -> Dict[str, List[Dict[str, Any]]]:
        """키워드별 샘플 관련 검색어 데이터 제공
        
        Args:
            keyword: 관련 검색어를 찾을 키워드
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: 샘플 관련 검색어 정보
        """
        result = {'top': [], 'rising': []}
        
        # 여기에 각 키워드별 샘플 데이터 정의
        # 예: 날씨, 뉴스, 코로나, 주식 등에 대한 샘플 데이터
        
        return result


# 캐시 유틸리티 함수
def get_cached_data(key: str) -> Optional[Any]:
    """캐시에서 데이터 가져오기
    
    Args:
        key: 캐시 키
        
    Returns:
        Optional[Any]: 캐시된 데이터 또는 None
    """
    if key in cache:
        timestamp, data = cache[key]
        # 캐시 타임아웃 확인
        if (datetime.now() - timestamp).seconds < CACHE_TIMEOUT:
            logger.info(f"캐시에서 '{key}' 데이터 가져옴")
            return data
    return None

def set_cached_data(key: str, data: Any) -> None:
    """데이터를 캐시에 저장
    
    Args:
        key: 캐시 키
        data: 저장할 데이터
    """
    cache[key] = (datetime.now(), data)
    logger.info(f"'{key}' 데이터를 캐시에 저장함")


# API 인스턴스 생성
trends_api = GoogleTrendsAPI()


# Flask 라우트
@app.route('/')
def index():
    """메인 페이지"""
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return render_template('index.html', current_time=current_time)

@app.route('/api/trends')
def get_trends():
    """실시간 인기 검색어 API"""
    # 캐시 확인
    cached_data = get_cached_data('trends')
    if cached_data:
        return jsonify(cached_data)
    
    # 데이터 가져오기
    trends = trends_api.get_realtime_trends()
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    result = {
        'trends': trends,
        'timestamp': current_time
    }
    
    # 캐시에 저장
    set_cached_data('trends', result)
    
    return jsonify(result)

@app.route('/api/related/<keyword>')
def get_related(keyword: str):
    """관련 검색어 API
    
    Args:
        keyword: 관련 검색어를 찾을 키워드
    """
    # 캐시 확인
    cache_key = f'related_{keyword}'
    cached_data = get_cached_data(cache_key)
    if cached_data:
        return jsonify(cached_data)
    
    # 데이터 가져오기
    related = trends_api.get_related_queries(keyword)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    result = {
        'keyword': keyword,
        'related': related,
        'timestamp': current_time
    }
    
    # 캐시에 저장
    set_cached_data(cache_key, result)
    
    return jsonify(result)


# 메인 실행 코드
if __name__ == '__main__':
    app.run(debug=True)