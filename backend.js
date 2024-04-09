import { Ai } from './vendor/@cloudflare/ai.js';

export default {
  async fetch(request, env) {
    const ai = new Ai(env.AI);
    let prompt;

    const headers = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST',
      'Access-Control-Allow-Headers': 'Content-Type, X-Secret-Key'
    };

    // Handle OPTIONS request
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers });
    }

    // Check for secret key in the request headers
    const secretKey = request.headers.get('X-Secret-Key');
    if (secretKey !== env.SECRET_KEY) {
      return new Response('Invalid secret key', { status: 403, headers });
    }

    if (request.method === 'POST') {
      const body = await request.json();
      prompt = body.prompt;
    } else {
      prompt = 'cyberpunk cat'; // default prompt for GET requests
    }

    const inputs = { prompt };

    const response = await ai.run('@cf/stabilityai/stable-diffusion-xl-base-1.0', inputs);

    headers['content-type'] = 'image/png';
    return new Response(response, { headers });
  }
};