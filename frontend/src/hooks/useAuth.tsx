// import { useState, useEffect } from 'react';
// import Cookies from 'js-cookie';
// import jwt_decode from 'jwt-decode';

// interface DecodedToken {
//     name: string;
//     sub: string;
//     exp: number;
// }

// export const useAuth = () => {
//     const [userName, setUserName] = useState<string | null>(null);

//     useEffect(() => {
//         const token = Cookies.get('jwt_token');
//         if (token) {
//             try {
//                 const decoded = jwt_decode(token) as DecodedToken;
//                 setUserName(decoded.name);
//             } catch (error) {
//                 console.error('Error decoding token:', error);
//             }
//         }
//     }, []);

//     return { userName, isAuthenticated: !!userName };
// };

export {}