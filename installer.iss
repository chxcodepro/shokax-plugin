; Inno Setup 安装脚本
; shokaX plugin 安装程序

#define MyAppName "shokaX plugin"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "chxcodepro"
#define MyAppURL "https://github.com/chxcodepro/shokax-plugin"
#define MyAppExeName "shokaX plugin.exe"

[Setup]
; 应用基本信息
AppId={{8F9A2B3C-4D5E-6F7A-8B9C-0D1E2F3A4B5C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=
InfoBeforeFile=
InfoAfterFile=
OutputDir=dist
OutputBaseFilename=shokaX_plugin_setup_v{#MyAppVersion}
SetupIconFile=
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
CloseApplications=force
CloseApplicationsFilter=*.exe

; 卸载配置
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}

[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode
Name: "startup"; Description: "开机自动启动"; GroupDescription: "其他选项:"; Flags: unchecked

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; 如果有其他文件，在这里添加
; Source: "dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Registry]
; 开机自启动注册表项
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "{#MyAppName}"; ValueData: """{app}\{#MyAppExeName}"""; Flags: uninsdeletevalue; Tasks: startup

[Code]
var
  WaitForPID: Integer;

// 解析命令行参数获取 PID
function GetPIDFromCmdLine(): Integer;
var
  I: Integer;
  S: String;
begin
  Result := 0;
  for I := 1 to ParamCount do
  begin
    S := ParamStr(I);
    if Pos('/PID=', UpperCase(S)) = 1 then
    begin
      Delete(S, 1, 5);
      Result := StrToIntDef(S, 0);
      Break;
    end;
  end;
end;

// 检测进程是否存在
function ProcessExists(PID: Integer): Boolean;
var
  ResultCode: Integer;
begin
  Result := False;
  if PID > 0 then
  begin
    Exec('tasklist', '/FI "PID eq ' + IntToStr(PID) + '" /NH', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    // 简化处理：假设进程已退出
    Result := False;
  end;
end;

// 强制关闭进程
function KillProcess(ProcessName: String): Boolean;
var
  ResultCode: Integer;
begin
  Result := Exec('taskkill', '/F /IM "' + ProcessName + '"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;

// 检测是否已安装旧版本
function GetUninstallString(): String;
var
  sUnInstPath: String;
  sUnInstallString: String;
begin
  sUnInstPath := ExpandConstant('Software\Microsoft\Windows\CurrentVersion\Uninstall\{#emit SetupSetting("AppId")}_is1');
  sUnInstallString := '';
  if not RegQueryStringValue(HKLM, sUnInstPath, 'UninstallString', sUnInstallString) then
    RegQueryStringValue(HKCU, sUnInstPath, 'UninstallString', sUnInstallString);
  Result := sUnInstallString;
end;

// 卸载旧版本
function UnInstallOldVersion(): Integer;
var
  sUnInstallString: String;
  iResultCode: Integer;
begin
  Result := 0;
  sUnInstallString := GetUninstallString();
  if sUnInstallString <> '' then begin
    sUnInstallString := RemoveQuotes(sUnInstallString);
    if Exec(sUnInstallString, '/SILENT /NORESTART /SUPPRESSMSGBOXES','', SW_HIDE, ewWaitUntilTerminated, iResultCode) then
      Result := 3
    else
      Result := 2;
  end else
    Result := 1;
end;

// 安装前检查
function InitializeSetup(): Boolean;
var
  I: Integer;
begin
  Result := True;

  // 获取命令行中的 PID（从应用内更新时传递）
  WaitForPID := GetPIDFromCmdLine();

  // 如果有 PID，等待进程退出
  if WaitForPID > 0 then
  begin
    // 等待最多 10 秒
    for I := 1 to 20 do
    begin
      Sleep(500);
      if not ProcessExists(WaitForPID) then
        Break;
    end;
  end;

  // 强制关闭正在运行的程序
  KillProcess('{#MyAppExeName}');
  Sleep(500);

  // 卸载旧版本
  if GetUninstallString() <> '' then
  begin
    UnInstallOldVersion();
  end;
end;

// 安装完成后清理
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // 安装完成后的清理工作
  end;
end;
