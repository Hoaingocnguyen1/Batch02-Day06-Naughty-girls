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
    let backendUrl = process.env.BACKEND_URL || 'http://127.0.0.1:8000';
    if (backendUrl.endsWith('/')) {
      backendUrl = backendUrl.slice(0, -1);
    }
    console.log("Next.js Proxy calling backend URL:", `${backendUrl}/api/chat`);

    const backendRes = await fetch(`${backendUrl}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Bypass-Tunnel-Reminder': 'true',     // Bỏ qua trang chào của localtunnel
        'ngrok-skip-browser-warning': 'true'  // Bỏ qua trang chào của ngrok (nếu dùng)
      },
      body: JSON.stringify(backendBody),
    });

    if (!backendRes.ok) {
      const errorText = await backendRes.text().catch(() => "");
      throw new Error(`Backend API returned status ${backendRes.status}. Response: ${errorText}`);
    }

    const data = await backendRes.json();
    return NextResponse.json(data);
  } catch (error: any) {
    console.error("Backend Proxy Error details:", {
      message: error?.message,
      cause: error?.cause,
      stack: error?.stack
    });
    return NextResponse.json({ 
      error: "Failed to connect to backend API", 
      details: error?.message 
    }, { status: 500 });
  }
}
