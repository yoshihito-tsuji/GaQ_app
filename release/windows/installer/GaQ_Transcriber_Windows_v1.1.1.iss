; GaQ Offline Transcriber v1.1.1 - Inno Setup Script
; Windows Installer Configuration

#define MyAppName "GaQ Offline Transcriber"
#define MyAppVersion "1.1.1"
#define MyAppPublisher "GaQ Project"
#define MyAppURL "https://github.com/yoshihito-tsuji/GaQ_app"
#define MyAppExeName "GaQ_Transcriber.exe"

[Setup]
; アプリケーション基本情報
AppId={{8F7A9B3C-2D1E-4A5B-9C8F-6E3D7A2B1C4E}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=
InfoBeforeFile=
InfoAfterFile=
; 出力設定
OutputDir=..\distribution
OutputBaseFilename=GaQ_Transcriber_Windows_v1.1.1_Setup
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
; アーキテクチャ
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
; 権限
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\GaQ_Transcriber\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\GaQ_Transcriber\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
