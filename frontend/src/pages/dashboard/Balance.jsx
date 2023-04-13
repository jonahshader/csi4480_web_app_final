import * as React from 'react';
import Link from '@mui/material/Link';
import Typography from '@mui/material/Typography';
import Title from './Title';

import { useStore } from 'src/main';

function preventDefault(event) {
  event.preventDefault();
}

export default function Balance() {
  const fname = useStore((s)=>s.data.fname)
  const balance = useStore((s)=>s.data.balance)
  // balance is an int in cents. need to convert to dollars and cents
  const dollars = Math.floor(balance / 100);
  const cents = balance % 100;
  return (
    <React.Fragment>
      <Title>{fname}'s Balance</Title>
      <Typography component="p" variant="h4">
        ${dollars}.{cents}
      </Typography>
      <Typography color="text.secondary" sx={{ flex: 1 }}>
      </Typography>
    </React.Fragment>
  );
}
