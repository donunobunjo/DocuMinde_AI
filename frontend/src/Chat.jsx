import React, {
    useState
} from "react";

import {
    sendMessageStream
} from "./api";


function Chat({
    sessionId,
    documentName
}) {

    const [messages, setMessages] =
        useState([]);

    const [input, setInput] =
        useState("");

    const [loading, setLoading] =
        useState(false);

    const [error, setError] =
        useState("");


    const handleSend = async () => {

        const question =
            input.trim();


        if (!question || loading) {
            return;
        }


        setError("");


        const userMessage = {

            role: "user",

            text: question

        };


        setMessages(
            previous => [
                ...previous,
                userMessage
            ]
        );


        setInput("");


        const botMessage = {

            role: "bot",

            text: "",

            sources: []

        };


        setMessages(
            previous => [
                ...previous,
                botMessage
            ]
        );


        setLoading(true);


        try {

            await sendMessageStream(

                sessionId,

                question,


                // ---------------------------------
                // Token received
                // ---------------------------------

                (token) => {

                    setMessages(
                        previous => {

                            const updated =
                                [...previous];


                            const lastIndex =
                                updated.length - 1;


                            updated[lastIndex] = {

                                ...updated[
                                    lastIndex
                                ],

                                text:
                                    updated[
                                        lastIndex
                                    ].text +
                                    token

                            };


                            return updated;
                        }
                    );

                },


                // ---------------------------------
                // Sources received
                // ---------------------------------

                (sources) => {

                    setMessages(
                        previous => {

                            const updated =
                                [...previous];


                            const lastIndex =
                                updated.length - 1;


                            updated[lastIndex] = {

                                ...updated[
                                    lastIndex
                                ],

                                sources:
                                    sources

                            };


                            return updated;
                        }
                    );

                }
            );


        } catch (error) {

            console.error(error);

            setError(
                error.message ||
                "Something went wrong."
            );

        } finally {

            setLoading(false);

        }
    };


    const handleKeyDown = (event) => {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            handleSend();

        }
    };


    return (

        <div className="chat-container">


            <div className="document-header">

                <div>

                    <strong>
                        📄 {documentName}
                    </strong>

                    <span>
                        Ready for questions
                    </span>

                </div>

            </div>


            <div className="chat-box">

                {messages.length === 0 && (

                    <div className="empty-chat">

                        <h3>
                            Ask your document
                        </h3>

                        <p>
                            Ask a question about
                            the information contained
                            in your uploaded PDF.
                        </p>

                    </div>

                )}


                {messages.map(
                    (message, index) => (

                        <div
                            key={index}
                            className={
                                `message ${message.role}`
                            }
                        >

                            <div className="bubble">

                                <div>
                                    {message.text}
                                </div>


                                {message.role ===
                                    "bot" &&

                                    message.sources &&
                                    message.sources.length >
                                    0 && (

                                        <div className="sources">

                                            <strong>
                                                Sources
                                            </strong>


                                            {message.sources.map(
                                                (
                                                    source,
                                                    sourceIndex
                                                ) => (

                                                    <div
                                                        key={
                                                            sourceIndex
                                                        }
                                                        className="source-item"
                                                    >

                                                        📄{" "}
                                                        {
                                                            source.document
                                                        }

                                                        {" — Page "}

                                                        {
                                                            source.page
                                                        }

                                                    </div>

                                                )
                                            )}

                                        </div>

                                    )}

                            </div>

                        </div>

                    )
                )}


                {loading && (

                    <div className="message bot">

                        <div className="bubble">

                            <div className="typing">

                                <span></span>
                                <span></span>
                                <span></span>

                            </div>

                        </div>

                    </div>

                )}

            </div>


            {error && (

                <div className="error-message">
                    {error}
                </div>

            )}


            <div className="chat-input-container">

                <textarea
                    className="chat-input"
                    value={input}
                    placeholder={
                        "Ask a question about your document..."
                    }
                    onChange={
                        event =>
                            setInput(
                                event.target.value
                            )
                    }
                    onKeyDown={
                        handleKeyDown
                    }
                    disabled={loading}
                    rows={2}
                />


                <button
                    className="primary-btn"
                    onClick={handleSend}
                    disabled={
                        loading ||
                        !input.trim()
                    }
                >

                    {loading
                        ? "Thinking..."
                        : "Send"
                    }

                </button>

            </div>

        </div>
    );
}


export default Chat;