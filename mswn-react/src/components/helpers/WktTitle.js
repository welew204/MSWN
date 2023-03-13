import React from "react";
import { useEffect, useRef } from "react";

export default function WktTitle({ title, onChange }) {
  const [editTitle, setEditTitle] = React.useState(false);

  const ref = useRef(null);

  const handleClickOutside = (event) => {
    if (ref.current && !ref.current.contains(event.target)) {
      setEditTitle(false);
    }
  };

  useEffect(() => {
    document.addEventListener("click", handleClickOutside, true);
    return () => {
      document.removeEventListener("click", handleClickOutside, true);
    };
  }, []);

  function handleEdit() {
    setEditTitle((prev) => !prev);
  }

  return (
    <div style={{ display: "flex", justifyContent: "center" }}>
      <p>{editTitle ? "Title:" : ""}</p>
      {editTitle ? (
        <input
          autoFocus
          ref={ref}
          className='editor--note-title-edit'
          style={{
            width: "90%",
            height: "45px",
            fontSize: "35px",
            fontWeight: "bold",
          }}
          type='text'
          onKeyDown={(event) => {
            event.keyCode == 13 ? setEditTitle(false) : void 0;
          }}
          id='title'
          name='title'
          onChange={(event) => onChange("workout_title", event.target.value)}
          value={title}></input>
      ) : (
        <h2 className='editor--note-title' onClick={handleEdit}>
          {title ? title : "Name Your Workout"}
        </h2>
      )}
    </div>
  );
}
