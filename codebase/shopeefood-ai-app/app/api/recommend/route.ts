import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    
    // Map frontend request structure to backend ChatRequest structure
    const backendBody = {
      message: body.message,
      history: body.history || [],
      context: {
        location: body.user_location ? {
          lat: body.user_location.lat,
          lng: body.user_location.lng
        } : null,
        current_time: new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit', hour12: false })
      }
    };

    // Forward the request to the FastAPI backend at /api/chat
    const backendUrl = process.env.BACKEND_URL || 'http://127.0.0.1:8000';
    const backendRes = await fetch(`${backendUrl}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(backendBody),
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
