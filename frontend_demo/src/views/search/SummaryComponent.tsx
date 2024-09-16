import React from 'react';

interface SummaryComponentProps {
    question: string;
    response: string;
}

const SummaryComponent: React.FC<SummaryComponentProps> = ({ question, response }) => {
    return (
        <div>
            <h2>Question: {question}</h2>
            <p>Summary: {response}</p>
        </div>
    );
};

export default SummaryComponent;
