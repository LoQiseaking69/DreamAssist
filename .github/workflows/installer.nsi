!define PRODUCT_NAME "DreamAssist"
!define PRODUCT_VERSION "1.0"
!define PRODUCT_PUBLISHER "HermiTech LLC"
!define PRODUCT_WEB_SITE "https://https://gamma.app/public/Welcome-to-HermiTech-L3C-a6ichx7iul82k4b?mode=doc/"
!include "MUI2.nsh"

!define MUI_ABORTWARNING
!define MUI_ICON "${{ github.workspace }}/Assets/Favicon.ico"
!define MUI_UNICON "${{ github.workspace }}/Assets/Favicon.ico"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "${{ github.workspace }}/Assets/Cjet.bmp"
!define MUI_WELCOMEFINISHPAGE_BITMAP "${{ github.workspace }}/Assets/Cjet.bmp"

!insertmacro MUI_LANGUAGE "English"

Section "DreamAssist Application" SEC_APPLICATION
  SetOutPath $INSTDIR
  File /r "dist\*.*"
  CreateShortCut "$DESKTOP\DreamAssist.lnk" "$INSTDIR\DreamAssist.exe"
SectionEnd

Function .onInit
  StrCpy $INSTDIR "$PROGRAMFILES\${PRODUCT_PUBLISHER}\${PRODUCT_NAME}"
  CreateDirectory $INSTDIR
FunctionEnd

Function un.onInit
  StrCpy $INSTDIR "$PROGRAMFILES\${PRODUCT_PUBLISHER}\${PRODUCT_NAME}"
FunctionEnd

Section "Uninstall"
  Delete "$INSTDIR\*.*"
  Delete "$DESKTOP\DreamAssist.lnk"
  RMDir "$INSTDIR"
SectionEnd
