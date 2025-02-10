PRAGMA foreign_keys = ON;

/* Table to store config values:
 * Standard name value pairs:
 *   dbversion = 1
 *   created = <ISO time string>
 */
 CREATE TABLE IF NOT EXISTS config (
  name  TEXT NOT NULL UNIQUE,
  value TEXT NOT NULL 
  );

/* The actual data; either X.509 certificates or OpenPGP
 * keyblocks.  */
 CREATE TABLE IF NOT EXISTS pubkey (
  /* The 20 octet truncated primary-fpr */
  ubid     BLOB NOT NULL PRIMARY KEY,
  /* The type of the public key: 1 = openpgp, 2 = X.509.  */
  type  INTEGER NOT NULL,
  /* The Ephemeral flag as used by gpgsm. Values: 0 or 1. */
  ephemeral INTEGER NOT NULL DEFAULT 0,
  /* The Revoked flag as set by gpgsm. Values: 0 or 1. */
  revoked INTEGER NOT NULL DEFAULT 0,
  /* The OpenPGP keyblock or X.509 certificate.  */
  keyblob BLOB NOT NULL
  );

/* Table with fingerprints and keyids of OpenPGP and X.509 keys.
 * It is also used for the primary key and the X.509 fingerprint
 * because we want to be able to use the keyid and keygrip.  */
 CREATE TABLE IF NOT EXISTS fingerprint (
  /* The fingerprint, for OpenPGP either 20 octets or 32 octets;
   * for X.509 it is the same as the UBID.  */
  fpr  BLOB NOT NULL PRIMARY KEY,
  /* The long keyid as a 64 bit blob.  */
  kid  BLOB NOT NULL,
  /* The keygrip for this key.  */
  keygrip BLOB NOT NULL,
  /* 0 = primary or X.509, > 0 = subkey.  Also used as
   * order number for the keys similar to uidno.  */
  subkey INTEGER NOT NULL,
  /* The Unique Blob ID (possibly truncated fingerprint).  */
  ubid BLOB NOT NULL REFERENCES pubkey
  );

/* Indices for the fingerprint table.  */
 CREATE INDEX IF NOT EXISTS fingerprintidx0 on fingerprint (ubid);
 CREATE INDEX IF NOT EXISTS fingerprintidx1 on fingerprint (fpr);
 CREATE INDEX IF NOT EXISTS fingerprintidx2 on fingerprint (keygrip);

/* Table to allow fast access via user ids or mail addresses.  */
 CREATE TABLE IF NOT EXISTS userid (
  /* The full user id - for X.509 the Subject or altSubject.  */
  uid  TEXT NOT NULL,
  /* The mail address if available or NULL.  */
  addrspec TEXT,
  /* The type of the public key: 1 = openpgp, 2 = X.509.  */
  type  INTEGER NOT NULL,
  /* The order number of the user id within the keyblock or
   * certificates.  For X.509 0 is reserved for the issuer, 1 the
   * subject, 2 and up the altSubjects.  For OpenPGP this starts
   * with 1 for the first user id in the keyblock.  */
  uidno INTEGER NOT NULL,
  /* The Unique Blob ID (possibly truncated fingerprint).  */
  ubid BLOB NOT NULL REFERENCES pubkey
  );

/* Indices for the userid table.  */
CREATE INDEX IF NOT EXISTS userididx0 on userid (ubid);
CREATE INDEX IF NOT EXISTS userididx1 on userid (uid);
CREATE INDEX IF NOT EXISTS userididx3 on userid (addrspec);

/* Table to allow fast access via s/n + issuer DN  (X.509 only).  */
CREATE TABLE IF NOT EXISTS issuer (
 /* The hex encoded S/N.  */
 sn TEXT NOT NULL,
 /* The RFC2253 issuer DN.  */
 dn TEXT NOT NULL,
 /* The Unique Blob ID (usually the truncated fingerprint).  */
 ubid BLOB NOT NULL REFERENCES pubkey
 );
CREATE INDEX IF NOT EXISTS issueridx1 on issuer (dn);
	