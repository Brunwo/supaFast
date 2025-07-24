
require('dotenv').config();
const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');

// Supabase project credentials
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseAnonKey = process.env.SUPABASE_ANON_KEY;

// Test user credentials
const email = process.env.TEST_EMAIL;
const password = process.env.TEST_PASSWORD;

const supabase = createClient(supabaseUrl, supabaseAnonKey);

async function getTestJwt() {
  console.log('Attempting to sign in with test credentials...');
  const { data, error } = await supabase.auth.signInWithPassword({
    email: email,
    password: password,
  });

  if (error) {
    console.error('Error signing in:', error.message);
    return;
  }

  if (data.session) {
    const accessToken = data.session.access_token;
    fs.writeFileSync('jwt.token', accessToken);
    console.log('Successfully retrieved JWT and saved it to jwt.token');
  } else {
    console.error('Could not retrieve session.');
  }
}

getTestJwt();
