# MyWindows

**MyWindows** is a tool that provides an intuitive interface for customizing various Windows settings and registry entries. It allows advanced control over trackpad, keyboard, and battery management, while also supporting backup and restoration of registry files. This tool is designed for users who want to streamline and personalize their Windows experience.

## Installation
- Download the `MyWindows.exe` file.

## Warning

### Tested Conditions:
This program has only been tested under two conditions:
- x86, Windows 11 Laptop, Intel Core Ultra 5 125H
- x86, Windows 11 Desktop, Ryzen 5 7500F CPU

### Unsupported Environments:
There is a high chance that the program may not function as intended under:
- ARM-based systems
- Windows 10 or earlier versions of Windows

### Local Machines
Be aware that this program edits registries of the local machine. Meaning, the adjustments made would apply not only to the current user of the device, but the entire device.

____________________________________________________________________________________

## Features

### Trackpads

#### 1. Curtains
Curtain zones refer to areas that have a lower sensitivity after keyboard use.
Non-curtain zones refer to areas that stay responsive during or immediately after keyboard use.

This feature could serve to improve the experience on palm rejection.

#### 2. Super Curtains
Super Curtains are the regions of the touchpad that do not trigger an input event. More specifically, these zones are set so that the user cannot start a user interaction from this zone.

This doesn't mean that this specific zone is disabled completely. If the user starts the touchpad use from a Non-Supercurtain zone (e.g., the center of the touchpad) and drag the finger to the edge (the supercurtain zone), the pointer will still react to the user input. 

What this disables are two things:
1. Input starting from the supercurtain zones
2. Tabs that occur at the supercurtain zones

#### 3. Right-click zone
As the name suggests, this controls the right click zone of the touchpad, beginning from the bottom-right corner of the trackpad. The Unit for this feature is in Percentage(%), unlike the units for the two featuers above, which are used in CM.

In addition, the percentage of the width is measured from the right edge in right-handed, and the left edge in left-handed configurations depending on how the mouse buttons option is set.

#### 4. Notes
The touchpad image provided for all three features is just an example, and the user should use the numbers of the slider and the input box as the accurate measurement.

In addition, all the edits made to your registry can be manually edited or deleted through the:  'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\PrecisionTouchPad' directory in the registry editor (regedit).
After editing/deleting the registry, make sure to reboot the device.

Refer to the link below for more information:
https://learn.microsoft.com/en-us/windows-hardware/design/component-guidelines/touchpad-tuning-guidelines


### Keyboards

#### 1. Key mapping
This feature uses the registry to remap a specific key into another key. More specifically, this remapping uses the registry and the scancode map to remap keys. According registry can be found under: 'HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Keyboard Layout' directory.
Deleting the Scancode Map registry and rebooting the device should restore the default settings.

#### 2. Hotkey(shortcuts) remapping
This feature serves to remap certain hotkeys into another combination of keys. One good example could be remapping Alt + Tab into Ctrl + Tab and vice versa. 

(This feature isn't complete)

One thing to note is that this feature doesn't use any registry. It uses the 'keyboard' library in Python. Meaning, the program should be running in the background for the remapping to work. This feature is enabled automatically by toggling the switch in the Hotkey remapping menu, thus running the functionality in a separate thread to minimize the consumption of resources.

#### 3. Note
There are multiple other applications that are already proven to be fail-safe (e.g., Microsoft powertoys, AutoHotKey, etc). However, I chose to implement this functionality simply for two reasons:
1. Willingness to integrate all customization features within a single program
2. Powertoys key remapping has certain bugs that impact my personal usage

In case of a failure or a significant bug that prevents you from resetting the settings in the program itself, please refer to the explanations above to set the settings to default. 

### Taskbar (Not made yet)

#### 1. Adjusting Width

#### 2. Adjusting transparency

#### 3. Adjusting roundness

### Battery

#### 1. Displaying battery charge/discharge rate
This feature displays the battery charge/discharge rate in the taskbar icon tray. The color of the icon is yellow if discharging and green if charging.

This feature, like the hotkey remapping feature, runs in a separate thread to minimize resource consumption.

You can always right-click the icon and disable the feature, or go into the settings menu to toggle the option.

___________________________________________________

Features to add:

features with a question mark are not necessary, implement if possible features.

All config info regarding the screen is dealt in configuration_manager.py

Trackpad
- Trackpad width and height customization: Should be able for the user to input the width and height of their own trackpad
- Hence, green/yellow area, along with the changed maximum width/height, should be adjusted (Same slider, but different max length and rate of change)

Keyboard
- Keymapping (Remapping) - completed
- Disabling certain keys - Not started (probably add it to Keymapping?)
- shortcuts - have to work on combinations and dynamic size for dropdown combobox (dynamic sizing for dropdown fixed)

Battery discharge rate
- Change polling rate - should be done in settings

Taskbar
- Control transparency
- Adjust the width/height of taskbar?

UI
- Rounded cornered windows
- Animation?
- Possible a theme to make the system more pleasing to watch

System
- Running in the background so that it consumes the least resources possible
- Registry path (Local machine vs User)

README
- Add images of actual use

Voltage/Clocks
- Last feature to be added, not sure if it's possible at the first place
- Adjusting voltages or clocks to allow for easy (underclocking/undervolting)


**Using a thread to run in background (IMPORTANT)**
- Battery drainage check
- Keyboard hotkeys remapping

If allowed by the user, these functions should be running in a separate thread from the main program that edits registries.

minimize instead of quit could replace this option maybe (check on resource usage)
--> 가급적이면 백그라운드 프로세스로 인식되도록 다른 쓰레드를 활용

_______________



Attribution: The only requirement of the MIT License is that you must include the original license notice in your project. This means that if you distribute your software (whether for free or for profit), you need to provide credit to the original author of CustomTkinter, typically by including a copy of the license in your product’s documentation.


MIT License attribute 해야됨 커스팀 tkinter 쓸꺼면
______________

custom tkinter 로 gui 업그레이드 완료, 주요 기능들 구현 완료

구현해야 되는거

레지스터 수정시 reboot prompt
save 누르면 백업할지 물어보는 기능 추가
노트북에서 기능테스트 한번 더

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