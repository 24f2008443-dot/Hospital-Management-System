// small helper for making api calls
async function apiGet(path) {
  const r = await fetch(path);
  return await r.json();
}

// apiGet('/api/doctors').then(d => console.log(d));
