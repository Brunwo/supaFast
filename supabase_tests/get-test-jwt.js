
const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');

// Supabase project credentials
const supabaseUrl = 'https://edhlshtkczpgmgraljgc.supabase.co';
const supabaseAnonKey  ='sb_publishable_uDQZM9e8-9i7WCIqLJpyng_UbZdnis5'

// Test user credentials : create from supabase UI
// turn captcha temporarly off in https://supabase.com/dashboard/project/<>/auth/protection

const email = 'test@test.com';
const password = 'testtest';

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
