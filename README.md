# adjust_reg
Program built to make registry editing easier.

자, 이제 슈퍼커튼이랑 커튼 조정까지 가능하게 만들었음 --> 이제는 이 두개를 edit 했을시,
1. 슈퍼 커튼과 커튼 창을 자동으로 닫고
2. 백업시 백업창을 열고, 백업을 하고, 백업창을 자동으로 닫고,
3. 메인메뉴만 떠 있겠지? --> 여기서 레지스트리 수정됐다, 컴퓨터 재부팅 제시

윈도우스케쥴러 통해서 UAC 없이 관리자 권한 부여하려고 했으나, 실패. main.exe로 한다면 될지 모르겠다.
_______________
자잘한 버그들

1. 창 위치 고정 + 사용하는 모니터 + 해상도에 맞춰서 작업표시줄에 안겹치는 선에서 우측하단에 고정 (g helper에서 inspired)
--> 다른 모니터에서도 잘 되는지 확인해봐야될듯? 일단 창 크기가 모니터 비율에 따라서 결정되긴 해야됨

new_ui_style을 통해서 모든 창을 scrollable하게 바꿈, 배율을 쓰면 살짝 깨지긴하는데 그거 제외하면 완성도 나쁘지않음. (기괴한 해상도 쓰면 아직 오른쪽이 잘리는 경우도 있다 --> 이건 모든 기능 만들고, 맨 마지막에 넣자.)

해야되는거
백업:
맨 위 칸은 반드시 모든 옵션을 0으로 되돌리는 옵션 (그냥 그 파일 미리 만들어놔도 될듯)

트랙패드 옵션 고치면 재시작 권하기
예쓰하면 바로 재시작

설정 만들기
터치패드 크기 설정 가능하게 하기
다음부터 킬때는 자동으로 관리자 권한 부여
백업파일 초기화

백업 파일에서 무슨 버튼을 클릭하던 자꾸 윈도우가 종료됨.

_______________

추가 아이디어:

키매핑

1. 시작 메뉴 검색 속도 향상
위치: HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced
변경: 새 DWORD(32비트) 값으로 DisabledSearchBoxSuggestions를 생성하고 값을 1로 설정합니다.
효과: 시작 메뉴 검색 시 불필요한 웹 검색 제안을 제거하여 검색 속도를 높일 수 있습니다.
2. 부팅 속도 향상 (메뉴 지연 시간 단축)
위치: HKEY_CURRENT_USER\Control Panel\Desktop
변경: MenuShowDelay 값을 400에서 100 또는 0으로 변경합니다.
효과: 메뉴의 지연 시간을 줄여 부드러운 사용자 경험을 제공합니다.
3. 최대 절전 모드 활성화/비활성화
위치: HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Power
변경: HibernateEnabled 값을 1로 변경하여 최대 절전 모드를 활성화하고, 0으로 설정하면 비활성화됩니다.
효과: 하드 드라이브 공간을 절약하거나 전원 옵션을 개선할 수 있습니다.
4. 작업 표시줄 미리보기 크기 조정
위치: HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Taskband
변경: MinThumbSizePx라는 DWORD(32비트) 값을 생성하고 원하는 크기(예: 100)를 입력합니다.
효과: 작업 표시줄 미리보기 창의 크기를 조정할 수 있습니다.
5. 드라이브 자동 숨김 (탐색기에서 특정 드라이브 숨기기)
위치: HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer
변경: NoDrives라는 DWORD 값을 추가하고, 숨기고자 하는 드라이브에 따라 값을 설정합니다.
효과: 탐색기에서 특정 드라이브를 숨길 수 있습니다.
6. 윈도우 업데이트 자동 재부팅 방지
위치: HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU
변경: NoAutoRebootWithLoggedOnUsers 값을 1로 설정하여 자동 재부팅을 방지합니다.
효과: 업데이트 후 자동으로 PC가 재부팅되는 것을 방지할 수 있습니다.
7. 파일 탐색기에서 "이 PC"에 대한 바로 가기 비활성화
위치: HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\MyComputer\NameSpace
변경: 여기서 원하지 않는 바로 가기 폴더의 하위 키를 삭제합니다.
효과: 파일 탐색기에서 "이 PC"에 표시되는 기본 바로 가기 항목을 제거할 수 있습니다.
8. Windows Defender 비활성화
위치: HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows Defender
변경: DisableAntiSpyware 값을 1로 설정하여 Windows Defender를 비활성화합니다.
효과: 다른 보안 프로그램을 사용할 경우 Windows Defender를 끌 수 있습니다.
9. 작업 표시줄의 투명도 활성화
위치: HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced
변경: UseOLEDTaskbarTransparency라는 DWORD(32비트) 값을 생성하고 값을 1로 설정합니다.
효과: 작업 표시줄의 투명도를 더 강화할 수 있습니다.
10. 콘텍스트 메뉴 항목 제거
위치: HKEY_CLASSES_ROOT\*\shellex\ContextMenuHandlers
변경: 특정 프로그램의 콘텍스트 메뉴 항목을 삭제할 수 있습니다.
효과: 우클릭 메뉴에서 불필요한 항목을 제거하여 간소화할 수 있습니다.
이 외에도 다양한 설정이 가능하지만, 잘못된 수정은 시스템 문제를 일으킬 수 있으므로 레지스트리 수정 전에 백업을 권장합니다.