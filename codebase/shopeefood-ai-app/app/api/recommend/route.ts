import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    
    // Forward the request to the FastAPI backend
    const backendRes = await fetch('http://127.0.0.1:8000/api/recommend', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    if (!backendRes.ok) {
      throw new Error(`Backend API returned status ${backendRes.status}`);
    }

    const data = await backendRes.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Backend Proxy Error:", error);
    return NextResponse.json({ error: "Failed to connect to backend API" }, { status: 500 });
  }
}
