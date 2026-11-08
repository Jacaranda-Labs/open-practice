# HTTPS access: unsupported protocol

Canonical address: **https://open-practice.open-practice.workers.dev/**

Use that literal address. Do not copy Markdown brackets, parentheses, a second URL, or add `www.`.

## Verified on 21 October 2026

An external check verified TLS 1.2 and TLS 1.3, hostname validation and HTTP 200 for Open Practice. Its certificate covered `*.zlnew.workers.dev` and was valid from 13 October 2026 to 11 January 2027. Google and Cloudflare public DNS returned the same IPv4 endpoints. The retired hostname redirected to the current site. Tapstall and DeskOS also passed the external TLS/HTTP check.

These observations do not establish what the affected laptop receives. The user reported that the failure followed that laptop across Wi-Fi and a phone hotspot. This increases suspicion of a device/browser/security-client issue but does not prove the cause.

## Safe steps on the affected laptop

1. Copy the canonical address above into the address bar, not a saved malformed link.
2. Check that the device's date, time and timezone are correct. Use the operating system's normal automatic-time setting if available.
3. Update the browser and the supported operating system, including certificate/root-store updates, then restart the browser.
4. Try another current browser on the same laptop. A private window can help isolate some browser state, but cannot repair unsupported OS cryptography.
5. Record the exact error code and browser/OS versions. A screenshot should omit personal data and account details.
6. If the problem persists across browsers and networks, ask the administrator or security-software vendor to inspect HTTPS interception, a managed proxy, VPN filtering and local certificate policy. Do not uninstall security software or bypass warnings as a routine workaround.
7. Compare access to another HTTPS site and another `workers.dev` site. Report which combinations fail. A device-wide interception policy may affect several sites; a healthy site elsewhere does not eliminate that possibility.

Do **not** enable obsolete SSL/TLS versions, disable certificate verification, expose credentials, switch account login to plain HTTP, or install a certificate supplied by an unfamiliar page.

TLS negotiation happens before the application can return HTML. Changing page JavaScript or adding an HTTP header cannot repair a handshake failure on the affected client. The managed `workers.dev` certificate is controlled by Cloudflare; no customer-zone SSL setting was changed.

## Read-only diagnostics

`python3 scripts/check-public-https.py` checks the listed sites from the machine where it runs. It verifies certificates and tests TLS 1.2/1.3 explicitly. It needs no credentials. A pass elsewhere is not a pass on the affected laptop.

For Windows, `scripts/diagnose-windows-https.ps1` prints basic non-secret diagnostics without changing network, certificate, browser or security settings. Run only if you are comfortable inspecting the file first. If execution policy blocks it, do not disable that policy merely for this test; provide the browser error screenshot instead. Remove any unexpected personal details before sharing output.

## Automation scope

At the initial HTTPS diagnosis the schedule performed retention cleanup only. Release 0.9.0 adds bounded daily organisational-contact research to that existing 03:00 UTC job, with invitation sending separately disabled because live Gmail authentication was rejected. New search results are unreviewed research, not automatic recipients. See [acquisition operations](acquisition-operations.md) for caps, source checks and current switches. TLS checks do not certify those business functions. No outreach messages were sent during the HTTPS diagnosis.
