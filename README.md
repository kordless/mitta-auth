# mitta-auth
Mitta Auth is a password-less authentication system written for Mitta.us. In this version, it is run on an AppEngine instance, but can be easily adapted to run standalone or on other obfuscated solutions such as Docker.

Authentication systems are apparantly difficult to implement. A simplified and secure authentication system is presented that prioritizes end user's rights while still remaining easy to implement and use by a developer.

## Passwords Aren't Needed
Over time, passwords become difficult to remember due to password requirements and may instead be stored by the user in various systems which themselves require passwords for access and which may be comprimised by other means. For example, one site used by a user may be comprimised which exposes that user's account on a second site because the user decided to use the same password, which the first site stored in plain text like a damn fool.

At the same time, on most sites, passwords may be "ignored" by using forgotten password functions and flow. No password is required to reset a password, usually. The typical mechanism to reset a password is to ether send the user a code via SMS, like Discord or Twilio does, or send the user an email with a reset link as most other sites do. Whether or not the site then logs in the user depends on hopefully remembering the right password.

Mitta Auth takes the less common approach and uses a "forgotten password" authentication flow to authenticate users quickly and easily. The user only types in a code or clicks on a link in their email client, which is typically open in an ajacent tab.

## 2FA Security
It is widely believed that SMS and email login functionality may be comprimised by attackers. In practice, more secure systems could be built by combining a token login with a 2FA login which can be reset seperately.  In the case of Coinbase, a reset of 2FA functionality requires a waiting period and gated on if the client used to reset the authentication system has been in recent communication with the system.

Mitta Auth will eventually implement both SMS and Google Authentication for logins. For the moment, the code implements only SMS and email authentication flows.

Because Mitta Auth uses an SMS auth flow, developers should be aware that SMS is not consiered a "safe" means of authentication for more advanced levels of security.

## Installing

## Configuring

## Example Use

