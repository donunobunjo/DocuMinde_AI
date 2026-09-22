import React, { useState } from "react";

import Upload from "./Upload";
import Chat from "./Chat";

import "./App.css";


function App() {

    const [sessionId, setSessionId] =
        useState(null);

    const [documentName, setDocumentName] =
        useState("");


    const handleUploadSuccess = (data) => {

        setSessionId(
            data.session_id
        );

        setDocumentName(
            data.filename
        );
    };


    return (

        <div className="app-container">

            <div className="card">

                <h1 className="title">
                    📄 DocuMind AI
                </h1>

                <p className="subtitle">
                    Ask questions about your documents
                </p>


                {!sessionId ? (

                    <Upload
                        onUploadSuccess={
                            handleUploadSuccess
                        }
                    />

                ) : (

                    <Chat
                        sessionId={sessionId}
                        documentName={
                            documentName
                        }
                    />

                )}

            </div>

        </div>
    );
}


export default App;