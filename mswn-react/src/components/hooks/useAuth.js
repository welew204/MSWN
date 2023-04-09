import { createContext, useContext, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { useLocalStorage } from "./useLocalStorage";

//from https://blog.logrocket.com/complete-guide-authentication-with-react-router-v6/

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useLocalStorage("user", null);
  const navigate = useNavigate();

  // call this function to authenticate a user
  // this needs some logic to actually query the server,
  // an endpoint that compares the string to the hashed version in the db
  // ??? or is there a best practice here?
  const login = async (data) => {
    // some logic
    setUser(data);
    console.log(data);
    navigate("/dashboard");
  };

  // call this function to sign out a logged in user
  const logout = () => {
    setUser(null);
    navigate("/", { replace: true });
  };

  const value = useMemo(
    () => ({
      user,
      login,
      logout,
    }),
    [user]
  );
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  return useContext(AuthContext);
};
