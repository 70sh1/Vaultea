#define MyAppName "Vaultea"
#define MyAppVersion "1.2"
#define RawVersion "1.2.0.0"
#define MyAppPublisher "yoshidzo"
#define MyAppURL "https://www.github.com/yoshidzo/Vaultea"
#define MyAppExeName "Vaultea.exe"

[Setup]
AppId={{73C3F812-182C-4D87-9B71-8AA7EA198365}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
VersionInfoVersion={#RawVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
UninstallDisplayIcon={app}\MyProg.exe
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
ShowLanguageDialog=auto
LicenseFile=..\..\LICENSE
PrivilegesRequired=lowest
OutputBaseFilename=Vaultea-installer-{#MyAppVersion}
SetupIconFile=..\..\resources\icons\vaultea.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}";

[Files]

Source: "dist\Vaultea\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

