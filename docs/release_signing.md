# 🔏 Windows Release Signing

By default, the pre-built executables are **not code-signed**. Windows SmartScreen will show a warning on first run for unsigned executables downloaded from the internet. See [Troubleshooting](troubleshooting.md#windows-smartscreen-blocks-the-executable) for the one-time bypass steps.

This page describes how to add code signing to the release workflow so that future releases are signed automatically.

!!! note "Signing is not currently active"
    The release workflow does not yet include signing steps. Follow the setup below to enable it.

---

## One-time setup

### 1. Generate a self-signed code-signing certificate

Run this in PowerShell on your machine (Administrator not required):

```powershell
$cert = New-SelfSignedCertificate `
  -Type CodeSigningCert `
  -Subject "CN=EncryptBIN" `
  -CertStoreLocation "Cert:\CurrentUser\My" `
  -KeyExportPolicy Exportable `
  -KeySpec Signature `
  -KeyLength 2048 `
  -HashAlgorithm SHA256 `
  -NotAfter (Get-Date).AddYears(5)

$pwd = ConvertTo-SecureString -String "YourStrongPassword" -Force -AsPlainText
$cert | Export-PfxCertificate -FilePath "EncryptBIN-signing.pfx" -Password $pwd
```

### 2. Base64-encode the PFX

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("EncryptBIN-signing.pfx")) | Set-Content "EncryptBIN-signing.b64.txt"
```

### 3. Add GitHub Secrets

In your repository: **Settings → Secrets and variables → Actions → New repository secret**

| Secret name | Value |
|---|---|
| `WINDOWS_CERT_PFX` | Full contents of `EncryptBIN-signing.b64.txt` |
| `WINDOWS_CERT_PASSWORD` | The password used above (`YourStrongPassword`) |

!!! danger "Delete local files after upload"
    Delete both `EncryptBIN-signing.pfx` and `EncryptBIN-signing.b64.txt` immediately after adding the secrets. **Never commit these files to the repository.**

---

## Adding signing steps to the workflow

Once the secrets are in place, add the following steps to the Windows build job in `.github/workflows/build_and_release.yaml`, after PyInstaller builds the `.exe`:

```yaml
- name: Sign binary (if certificate present)
  if: ${{ secrets.WINDOWS_CERT_PFX != '' }}
  run: |
    $pfxBytes = [Convert]::FromBase64String("${{ secrets.WINDOWS_CERT_PFX }}")
    [IO.File]::WriteAllBytes("signing.pfx", $pfxBytes)

    & "C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe" sign `
      /fd SHA256 `
      /td SHA256 `
      /tr http://timestamp.digicert.com `
      /f signing.pfx `
      /p "${{ secrets.WINDOWS_CERT_PASSWORD }}" `
      "dist\EncryptBIN.exe"

    Remove-Item signing.pfx
```

Apply the same step after building the Inno Setup installer to sign `EncryptBIN-windows-setup.exe` as well.

The DigiCert RFC 3161 timestamp (`/tr`) ensures the signature remains valid after the certificate expires.

---

## Limitations of a self-signed certificate

A self-signed certificate is **not trusted by Windows by default**. SmartScreen will still warn users who have not installed the certificate manually. Over time, as more users download and run the app, Microsoft may build enough reputation data to suppress the warning automatically.

For fully transparent installs with no warning, you need a certificate issued by a trusted CA (e.g. DigiCert, Sectigo) or an EV (Extended Validation) certificate.

### Install the cert on a controlled machine (internal use)

For teams that control their own machines, install the certificate once per machine to permanently suppress the SmartScreen prompt:

```powershell
# Run as Administrator
Import-PfxCertificate `
  -FilePath "EncryptBIN-signing.pfx" `
  -CertStoreLocation "Cert:\LocalMachine\TrustedPublisher" `
  -Password (ConvertTo-SecureString "YourStrongPassword" -Force -AsPlainText)
```
