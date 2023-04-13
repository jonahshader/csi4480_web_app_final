import * as React from 'react';
import Link from '@mui/material/Link';
import Typography from '@mui/material/Typography';
import Title from './Title';

import { useStore, router } from 'src/main';

let inputAmount = 0;
let destEmail = '';

export default function Transfer() {
    const user_token = useStore((s)=>s.user_token)
    const fetchData = useStore((s)=>s.fetchData)
    const [success, setSuccess] = React.useState('')

    const transfer = async (amount) => {
        // amount is in the format 0.00
        // convert amount to cents
        const cents = Math.round(amount * 100);
        const response = await fetch(`http://localhost:8000/transfer?user_token=${user_token}&dest_email=${destEmail}&amount=${cents}`, {
            method: 'PUT',
            'Content-Type': 'application/json',
        });

        const data = await response.json();

        if (data['token_expired']) {
            router.navigate('/sign-in');
        } else if (data['success']) {
            setSuccess('Success!');
        } else {
            setSuccess('Failed!');
        }

        fetchData();
    }

    return (
        <React.Fragment>
            <Title>
                Transfer
            </Title>
            <Typography component="p" variant="h4">
                <input type="number" step="0.01" onChange={(e) => inputAmount = e.target.value} />
                <input type="text" onChange={(e) => destEmail = e.target.value} />
                <button onClick={() => transfer(inputAmount)}>Transfer</button>
            </Typography>
            <Typography color="text.secondary" sx={{ flex: 1 }}>
                {success}
            </Typography>
        </React.Fragment>
    )
}