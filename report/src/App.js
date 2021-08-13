import React from 'react';
import CssBaseline from '@material-ui/core/CssBaseline';
import Typography from '@material-ui/core/Typography';
import {createTheme, makeStyles, ThemeProvider} from '@material-ui/core/styles';
import Container from '@material-ui/core/Container';
import Link from '@material-ui/core/Link';
import Graph from './Graph';
import new_york_graph from './new_york_graph.json';

function Copyright() {
  return (
    <Typography variant="body2" color="textSecondary">
      {'Copyright © '}
      <Link color="inherit" href="https://material-ui.com/">
        John Cunniff
      </Link>{' '}
      {new Date().getFullYear()}
      {'.'}
    </Typography>
  );
}

const theme = createTheme({
  palette: {
    type: 'dark',
  },
})

const useStyles = makeStyles((theme) => ({
  root: {
    display: 'flex',
    flexDirection: 'column',
    minHeight: '100vh',
  },
  top: {
    marginTop: theme.spacing(8),
  },
  main: {
    marginTop: theme.spacing(5),
  },
  footer: {
    padding: theme.spacing(3, 2),
    marginTop: 'auto',
    backgroundColor: theme.palette.grey[800],
  },
  subtitle: {
    marginTop: theme.spacing(3),
  },
  body: {
    textIndent: theme.spacing(2),
    margin: theme.spacing(1),
  },
}));

function SubTitle({children}) {
  const classes = useStyles();
  return (
    <Typography variant={'h4'} className={classes.subtitle}>
      {children}
    </Typography>
  );
}

function Body({children}) {
  const classes = useStyles();
  return (
    <Typography variant="body1" className={classes.body}>
      {children}
    </Typography>
  )
}


function App() {
  const classes = useStyles();

  return (
    <div className={classes.root}>
      <ThemeProvider theme={theme}>
        <CssBaseline/>

        <Container className={classes.top} maxWidth="md">
          <Typography variant="h2" component="h1" gutterBottom>
            A Journey into Alien Numbers in the 1940s
          </Typography>
          <Typography variant="h4">
            HIST 175 Final Project
          </Typography>
          <Typography variant="h5" component="h2" gutterBottom>
            By John Cunniff
          </Typography>
        </Container>

        <Container component="main" className={classes.main} maxWidth="md">
          <SubTitle>
            A Numbers
          </SubTitle>
          <Body>
            Alien Numbers (or A number for short) are identifier numbers that are assigned by the US government to
            any and all immigrants. The numbers are tracked by the United States Citizenship and Immigration Services.
            A numbers are used like case numbers to track things like citizenship, or visa applications.
          </Body>

          <SubTitle>
            Sequential A Numbers
          </SubTitle>
          <Body>
            An interesting question to ask is how exactly these numbers are allocated. As with many things in the United
            States government, it has changed drastically over the decades. The time period that is quite interesting
            is 1940-1945. During that time, A numbers were often allocated in sequence by the INS in washington DC.
            This lead to situations where groups of immigrants that were assigned consecutive A numbers may have
            been in the same line at the same office on the same day.
          </Body>
          <Body>
            During this time period some families would all apply for visas at the same time, and have sequential A
            numbers assigned to them.
          </Body>

          <SubTitle>
            The Data
          </SubTitle>
          <Body>
            Publicly available historical immigration data is sparse to say the least. There are very few official
            sources that make any data available.
          </Body>
          <Body>
            One such place is the United States National Archive or NARA for short. NARA makes select immigration
            records available, but only for people that are or would be at least 100 years of age.
          </Body>

          <SubTitle>
            Graph Analysis
          </SubTitle>
          <Body>
            Knowing that sequential A numbers many have some meaning gives insight into the data. A simple and
            effective way of turning this insight into visualization humans can understand is by turning the data
            into a simple graph. A graph is just a bunch of points that represent a certain thing, and connections
            between them. The end result is some kind of a "network" of nodes with some implied meaning.
          </Body>
          <Body>
            For this problem the topology of the graph that we want to create is the most important thing. The topology
            is just the layout. It is deciding what becomes a node, and what becomes a connection.
          </Body>
          <Body>
            There are several valid options for the topology of the graph
          </Body>

          <Graph
            title={'New York Graph'}
            data={new_york_graph}
          />

          <Graph
            title='test'
            data={{
              nodes: [{id: 'root', type: 'root'}, {id: 'loc', type: 'location'}],
              links: [{source: 'root', target: 'loc'}],
            }}
          />
        </Container>

        <footer className={classes.footer}>
          <Container maxWidth="sm">
            <Typography variant="body1">
              My sticky footer can be found here.
            </Typography>
            <Copyright/>
          </Container>
        </footer>
      </ThemeProvider>
    </div>
  );
}

export default App;
