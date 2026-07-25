; PlaylistForge Inno Setup installer script
; Requires Inno Setup 6+ (https://jrsoftware.org/isinfo.php)
; Build: iscc packaging\windows\playlistforge.iss

#define MyAppName "PlaylistForge"
#define MyAppVersion "0.5.0"
#define MyAppPublisher "PlaylistForge Contributors"
#define MyAppURL "https://github.com/playlistforge/playlistforge"
#define MyAppExeName "PlaylistForge.exe"

[Setup]
AppId={{B8F4A3D2-1C4E-4F6A-9B8C-3D2E1F0A5B7C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=..\..\LICENSE
OutputDir=..\..\dist
OutputBaseFilename=PlaylistForge-Setup-{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce

[Files]
Source: "..\..\dist\PlaylistForge\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "{app}\PlaylistForge.exe"; Parameters: "--uninstall"; Flags: runhidden

[Code]
function InitializeSetup: Boolean;
begin
  Result := True;
end;
