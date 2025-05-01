// Simple fetch test for API endpoints
const fetch = require('node-fetch');

const API_URL = 'http://localhost:8000';

async function testAPI() {
  console.log('Testing API endpoints...');
  
  // Test the recommendations endpoint
  try {
    console.log('Testing /recommendations/user1 endpoint...');
    const recResponse = await fetch(`${API_URL}/recommendations/user1`);
    if (!recResponse.ok) {
      throw new Error(`HTTP error! status: ${recResponse.status}`);
    }
    const recData = await recResponse.json();
    console.log('Recommendations response:', JSON.stringify(recData, null, 2));
  } catch (error) {
    console.error('Error testing recommendations endpoint:', error);
  }

  // Test the products endpoint
  try {
    console.log('\nTesting /products endpoint...');
    const prodResponse = await fetch(`${API_URL}/products`);
    if (!prodResponse.ok) {
      throw new Error(`HTTP error! status: ${prodResponse.status}`);
    }
    const prodData = await prodResponse.json();
    console.log(`Products response: Retrieved ${prodData.length} products`);
    if (prodData.length > 0) {
      console.log('First product:', JSON.stringify(prodData[0], null, 2));
    }
  } catch (error) {
    console.error('Error testing products endpoint:', error);
  }
  
  // Test health endpoint
  try {
    console.log('\nTesting /health endpoint...');
    const healthResponse = await fetch(`${API_URL}/health`);
    if (!healthResponse.ok) {
      throw new Error(`HTTP error! status: ${healthResponse.status}`);
    }
    const healthData = await healthResponse.json();
    console.log('Health response:', JSON.stringify(healthData, null, 2));
  } catch (error) {
    console.error('Error testing health endpoint:', error);
  }
}

testAPI(); 