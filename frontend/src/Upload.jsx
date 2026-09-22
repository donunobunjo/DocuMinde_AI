import React, { useState } from "react";

import { uploadFile } from "./api";


function Upload({ onUploadSuccess }) {

    const [file, setFile] =
        useState(null);

    const [loading, setLoading] =
        useState(false);

    const [error, setError] =
        useState("");


    const handleFileChange = (event) => {

        const selectedFile =
            event.target.files[0];

        setError("");

        if (!selectedFile) {
            setFile(null);
            return;
        }


        if (
            selectedFile.type !==
            "application/pdf"
        ) {

            setError(
                "Please select a PDF file."
            );

            setFile(null);

            return;
        }


        setFile(selectedFile);
    };


    const handleUpload = async () => {

        if (!file) {

            setError(
                "Please select a PDF file first."
            );

            return;
        }


        setLoading(true);
        setError("");


        try {

            const data =
                await uploadFile(file);


            onUploadSuccess(data);

        } catch (error) {

            console.error(error);

            setError(
                error.message ||
                "Upload failed."
            );

        } finally {

            setLoading(false);

        }
    };


    return (

        <div className="upload-section">

            <h2>
                Upload a PDF
            </h2>


            <p className="upload-description">
                Upload a document and ask
                questions about its content.
            </p>


            <input
                className="file-input"
                type="file"
                accept=".pdf,application/pdf"
                onChange={
                    handleFileChange
                }
            />


            {file && (

                <p className="selected-file">
                    Selected: {file.name}
                </p>

            )}


            {error && (

                <div className="error-message">
                    {error}
                </div>

            )}


            {loading && (

                <div className="processing-message">
                    Processing document...
                </div>

            )}


            <button
                className="primary-btn"
                onClick={handleUpload}
                disabled={
                    loading ||
                    !file
                }
            >

                {loading
                    ? "Processing..."
                    : "Upload Document"
                }

            </button>

        </div>
    );
}


export default Upload;