import { NextResponse } from 'next/server';

// Configuration
const TOKEN_SERVER_URL = process.env.NEXT_PUBLIC_TOKEN_SERVER_URL || 'http://localhost:8002';
const LIVEKIT_URL = process.env.LIVEKIT_URL;

// don't cache the results
export const revalidate = 0;

export type ConnectionDetails = {
  serverUrl: string;
  roomName: string;
  participantName: string;
  participantToken: string;
};

export async function GET() {
  try {
    if (LIVEKIT_URL === undefined) {
      throw new Error('LIVEKIT_URL is not defined');
    }

    // Generate test user data
    const timestamp = Date.now();
    const participantName = `Test Patient ${timestamp}`;
    const userEmail = `patient-${timestamp}@test.com`;
    const roomName = `appointment-test-${timestamp}`;

    // Request token from our token server
    const tokenResponse = await fetch(`${TOKEN_SERVER_URL}/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_email: userEmail,
        full_name: participantName,
        room_name: roomName,
      }),
    });

    if (!tokenResponse.ok) {
      throw new Error(`Token server responded with: ${tokenResponse.status} ${tokenResponse.statusText}`);
    }

    const tokenData = await tokenResponse.json();

    // Return connection details
    const data: ConnectionDetails = {
      serverUrl: LIVEKIT_URL,
      roomName: tokenData.room_name,
      participantToken: tokenData.token,
      participantName,
    };
    
    const headers = new Headers({
      'Cache-Control': 'no-store',
    });
    return NextResponse.json(data, { headers });
  } catch (error) {
    if (error instanceof Error) {
      console.error(error);
      return new NextResponse(error.message, { status: 500 });
    }
  }
}
