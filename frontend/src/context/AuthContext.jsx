import {useContext,createContext,useState,useEffect} from 'react';
import apiService from './../services/api.js'


const AuthContext = createContext();

const useAuth = () =>{
    const context = useContext(AuthContext);
    if(!context){
        throw new Error('useAuth must be used inside AuthProvider')
    }
    return context;
}

const AuthProvider = ({children}) =>{

    const [user,setUser] = useState(null);
    const [loading,setLoading] = useState(true);
    const [isAuthenticated, setIsAuthenticated] = useState(false);


    useEffect(()=>{
        const checkAuth = async() =>{
            const token = localStorage.get('AuthToken')
            if(token){
                try{
                    const userData = await apiService.getUserData();
                    setUser(userData);
                    setIsAuthenticated(true)
                }catch(error){
                    console.log("Error checking auth");
                    localStorage.remove('AuthToken');
                    apiService.setToken(null)

                }
                

            }

            setLoading(false);
        }

        checkAuth();
    },[])

    const login = async (email,password) =>{
        //eslint-disable-next-line no-useless-catch
        try{
            const userData = await apiService.login(email,password)
            setUser(userData);
            setIsAuthenticated(true);

        }catch(error){
            throw error;
        }

    }
    const register = async (email,password,display_name) =>{
        
    }

}