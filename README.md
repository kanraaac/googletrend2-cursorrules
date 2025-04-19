# Google Trends 애플리케이션을 위한 Cursor AI 규칙

이 저장소는 Google Trends 데이터를 수집하고 분석하는 Python 웹 애플리케이션을 개발할 때 Cursor AI 에디터의 성능을 최적화하기 위한 `.cursorrules` 파일을 제공합니다.

## 왜 이 규칙 파일을 사용해야 하나요?

이 `.cursorrules` 파일은 다음과 같은 이점을 제공합니다:

1. **Google Trends API 최적화**: Google Trends API 요청 제한, 에러 처리, 데이터 정제 등에 대한 최선의 접근 방식을 제안합니다.
2. **성능 및 안정성 향상**: 요청 간격 조정, 캐싱 전략, 대체 데이터 제공 등을 통해 애플리케이션의 안정성을 높입니다.
3. **코드 표준 준수**: Python 및 Flask 모범 사례를 따르는 일관된 코딩 스타일을 보장합니다.
4. **유지보수성 향상**: 명확한 모듈 구조, 상세한 문서화, 타입 힌팅 등을 통해 코드의 유지보수성을 향상시킵니다.
5. **사용자 경험 개선**: 관련 검색어, 시각화, 데이터 비교 등 Google Trends 데이터를 효과적으로 활용하는 방법을 제안합니다.

## 이 규칙 파일의 주요 특징

- Python, Flask, pytrends, pandas 등 Google Trends 애플리케이션을 위한 주요 기술 스택 최적화
- API 요청 제한 관리 및 에러 처리에 대한 구체적인 가이드라인
- Google Trends 데이터의 효과적인 시각화 및 분석 전략
- Flask 웹 애플리케이션 모범 사례 적용
- 타입 힌팅, 명확한 문서화, 예외 처리 등 코드 품질 향상 방법

## 사용 방법

1. [Cursor AI](https://cursor.sh/)를 설치합니다.
2. 이 저장소에서 `.cursorrules` 파일을 다운로드합니다.
3. Google Trends 관련 프로젝트의 루트 디렉토리에 다운로드한 `.cursorrules` 파일을 복사합니다.
4. Cursor AI에서 프로젝트를 열면 자동으로 규칙이 적용됩니다.
5. 필요에 따라 프로젝트에 맞게 규칙을 커스터마이즈할 수 있습니다.

## 최적화된 애플리케이션 구조 예시

```
googletrend-app/
├── .cursorrules            # Cursor AI 규칙 파일
├── app.py                  # Flask 애플리케이션 진입점
├── google_trends.py        # Google Trends API 래퍼 및 데이터 수집 로직
├── templates/              # HTML 템플릿
│   ├── index.html
│   └── trend_details.html
├── static/                 # 정적 파일 (CSS, JS, 이미지 등)
│   ├── css/
│   ├── js/
│   └── img/
├── utils/                  # 유틸리티 함수
│   ├── cache.py            # 캐싱 메커니즘
│   └── data_processing.py  # 데이터 처리 및 정제
├── models/                 # 데이터 모델 (선택적)
├── requirements.txt        # 의존성 목록
└── README.md               # 프로젝트 문서
```

## 라이선스

이 프로젝트는 MIT 라이선스 하에 제공됩니다. 자세한 내용은 LICENSE 파일을 참조하세요.

## 기여

이 규칙 파일에 대한 개선 제안이나 버그 리포트는 언제든지 환영합니다. Pull request를 통해 기여하거나 Issues 탭에서 문제를 보고해 주세요.