import React, { useEffect, useState } from "react";

const Typewriter = ({ text = "", speed = 100, onComplete }) => {
  const [displayedText, setDisplayedText] = useState("");

  useEffect(() => {
    let index = 0;

    const interval = setInterval(() => {
      if (index >= text.length) {
        clearInterval(interval);
        if (onComplete) onComplete();
        return;
      }

      setDisplayedText((prev) => prev + text.charAt(index));
      index++;
    }, speed);

    return () => clearInterval(interval);
  }, [text, speed, onComplete]);

  return <span>{displayedText}</span>;
};

export default Typewriter;
