const API_URL = import.meta.env.VITE_API_URL;

if (!API_URL) {
    throw new Error("VITE_API_URL is not configured.");
}


// ======================================================
// Upload PDF
// ======================================================

export const uploadFile = async (file) => {

    const formData = new FormData();

    formData.append("file", file);

    const response = await fetch(
        `${API_URL}/upload/`,
        {
            method: "POST",
            body: formData
        }
    );

    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            data.detail || "Document upload failed."
        );
    }

    return data;
};


// ======================================================
// Streaming chat
// ======================================================

export const sendMessageStream = async (
    sessionId,
    message,
    onToken,
    onSources
) => {

    const response = await fetch(
        `${API_URL}/chat/stream`,
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                session_id: sessionId,
                query: message
            })
        }
    );

    if (!response.ok) {

        let errorMessage = "Failed to send message.";

        try {
            const data = await response.json();

            errorMessage =
                data.detail || errorMessage;

        } catch {
            // Keep default error message
        }

        throw new Error(errorMessage);
    }


    if (!response.body) {
        throw new Error(
            "Streaming is not supported by this browser."
        );
    }


    const reader =
        response.body.getReader();

    const decoder =
        new TextDecoder("utf-8");

    let buffer = "";


    while (true) {

        const {
            value,
            done
        } = await reader.read();


        if (done) {
            break;
        }


        buffer += decoder.decode(
            value,
            {
                stream: true
            }
        );


        const events =
            buffer.split("\n\n");


        buffer =
            events.pop() || "";


        for (const event of events) {

            const line =
                event
                    .split("\n")
                    .find(
                        line =>
                            line.startsWith("data:")
                    );


            if (!line) {
                continue;
            }


            const jsonData =
                line
                    .replace("data:", "")
                    .trim();


            if (!jsonData) {
                continue;
            }


            try {

                const data =
                    JSON.parse(jsonData);


                if (data.type === "token") {

                    onToken(
                        data.content
                    );

                }


                else if (
                    data.type === "sources"
                ) {

                    if (onSources) {

                        onSources(
                            data.sources
                        );

                    }

                }


                else if (
                    data.type === "error"
                ) {

                    throw new Error(
                        data.message
                    );

                }

            } catch (error) {

                console.error(
                    "SSE parsing error:",
                    error
                );

            }
        }
    }
};