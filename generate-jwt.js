#!/usr/bin/env node
const jwt = require("jsonwebtoken");
require("dotenv").config(); // To load SUPABASE_JWT_SECRET from .env if --secret is not used

// CLI arguments parser
const yargs = require("yargs/yargs");
const { hideBin } = require("yargs/helpers");

const argv = yargs(hideBin(process.argv))
  .option("role", {
    alias: "r",
    type: "string",
    description: "Role to include in the token",
    demandOption: true, // Role is mandatory
  })
  .option("expiry", {
    alias: "e",
    type: "string",
    description: 'Token expiry (e.g., "2h", "1d")',
    default: "1h",
  })
  .option("subject", {
    alias: "s",
    type: "string",
    description: "Subject (usually user ID)",
    default: "system-generated-user", // Changed default to be more descriptive
  })
  .option("debug", { // Renamed from 'd' to 'debug' for clarity in usage, kept alias 'd'
    alias: "d",
    type: "boolean",
    description: "Enable debug output (shows token and decoded payload)",
    default: false,
  })
  .option("secret", {
    alias: "k", // 'k' for key
    type: "string",
    description: "JWT secret key (overrides SUPABASE_JWT_SECRET from .env)",
  })
  .help()
  .alias('h', 'help')
  .argv;

function generateToken(role, expiry, subject, isAnonymous = false, email = null) {
  const secretKey = argv.secret || process.env.SUPABASE_JWT_SECRET;

  if (!secretKey) {
    console.error(
      "Error: JWT secret not provided. Use --secret <your_secret> or set SUPABASE_JWT_SECRET in your .env file."
    );
    process.exit(1);
  }
  if (secretKey.length < 32 && argv.debug) {
    console.warn("Warning: JWT secret is less than 32 characters long. This is not recommended for production.");
  }


  const payload = {
    sub: subject,
    role: role,
    iss: "supabase-jwt-generator", // Added an issuer claim
    iat: Math.floor(Date.now() / 1000), // Issued at timestamp
    // Standard Supabase claims (can be customized or omitted if not needed for your tests)
    aud: "authenticated", // Default audience for Supabase
    is_anonymous: isAnonymous,
    // email: email || `${subject}@example.com`, // Construct a dummy email if not provided
  };

  // Conditionally add email if provided or if subject suggests it's a user
  if (email) {
    payload.email = email;
  } else if (subject !== "system-generated-user" && !isAnonymous) {
    payload.email = `${subject.replace(/[^a-zA-Z0-9]/g, '_')}@example.com`;
  }


  try {
    const token = jwt.sign(payload, secretKey, { expiresIn: expiry });
    return token;
  } catch (error) {
    console.error("Error generating token:", error.message);
    if (argv.debug) {
      console.error("Payload:", payload);
      console.error("Secret used:", secretKey ? `${secretKey.substring(0, 3)}... (length: ${secretKey.length})` : "Not provided");
    }
    process.exit(1);
  }
}

// Generate and output the token
const token = generateToken(argv.role, argv.expiry, argv.subject);

if (argv.debug) { // Corrected to use argv.debug
  console.log("\nGenerated JWT Token:");
}
console.log(token); // Always print the token

if (argv.debug) { // Corrected to use argv.debug
  console.log("\nDecoded Payload (verification not performed by decode):");
  try {
    console.log(JSON.stringify(jwt.decode(token), null, 2));
    // Optionally, verify for debugging (though sign should ensure it's valid with the same key)
    // const verified = jwt.verify(token, argv.secret || process.env.SUPABASE_JWT_SECRET);
    // console.log("\nVerified Payload (for debug):");
    // console.log(JSON.stringify(verified, null, 2));
  } catch (e) {
    console.error("\nError decoding/verifying token for debug output:", e.message);
  }
}
