# Week 11 실습

## 오늘 한 것
- PyInstaller 설치 및 빌드
- resource_path() 함수 추가
- --add-data 옵션으로 에셋 포함
- .exe 실행 확인

## resource_path() 를 써야 하는 이유
보통 개발 중에는 이미지나 사운드 에셋을 pygame.'image/sound'.load("assets/player.'png/wav'")로 불러오지만
이것을 pyinstaller로 빌드하면 내부 구조가 바뀌어서 경로가 더 이상 제대로 동작하지 않는 경우가 생기는데
이 때 resource_path()를 쓰면 exe로 빌드해도 정상 동작이 가능하게 만들어주기 때문에 resource_path()를 써야한다.

## 빌드 명령어
pyinstaller main.py

pyinstaller --onefile --windowed --add-data "assets;assets" --name=Hungry_Slime main.py

## AI 활용 내역 
없음
