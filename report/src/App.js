import React from 'react';
import CssBaseline from '@material-ui/core/CssBaseline';
import Typography from '@material-ui/core/Typography';
import {createTheme, makeStyles, ThemeProvider} from '@material-ui/core/styles';
import Container from '@material-ui/core/Container';
import Link from '@material-ui/core/Link';
import Graph from './Graph';
import IconButton from '@material-ui/core/IconButton';
import {DataGrid} from '@material-ui/data-grid';
import Paper from '@material-ui/core/Paper';

import filtered_data from './filtered_data.json';
import new_york_graph_branch from './new_york_graph_branch.json';
import new_york_graph_branch_link from './new_york_graph_branch_link.json';
import new_york_graph_branch_link_clean from './new_york_graph_branch_link_clean.json';

import GitHubIcon from '@material-ui/icons/GitHub';
import LinkIcon from '@material-ui/icons/Link';
import GetAppIcon from '@material-ui/icons/GetApp';

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
    marginBottom: theme.spacing(5),
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
  linkIcon: {
    padding: theme.spacing(1),
  },
  dataPaper: {
    padding: theme.spacing(1),
    height: 700,
  },
}));

function downloadTextFile(filename, text, content_type) {
  const element = document.createElement('a');
  element.hidden = true;
  const file = new Blob([text], {type: content_type});
  element.href = URL.createObjectURL(file);
  element.download = filename;
  document.body.appendChild(element);
  element.click();
}


function SubTitle({children}) {
  const classes = useStyles();
  const id = children.toString().toLowerCase().replaceAll(' ', '_');
  return (
    <div style={{display: 'flex', alignItems: 'center'}} className={classes.subtitle}>
      <IconButton size={'small'} href={'#' + id} className={classes.linkIcon}>
        <LinkIcon/>
      </IconButton>
      <Typography variant={'h4'} id={id}>
        {children}
      </Typography>
    </div>
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
            Sequential Alien Numbers in the mid 1940s
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
            Historical Context - Sequential A Numbers
          </SubTitle>
          <Body>
            An interesting question to ask is how exactly these numbers are allocated. As with many things in the United
            States government, it has changed drastically over the decades. The time period that is quite interesting
            is 1940-1945. During that time, A numbers were often allocated in sequence by the INS in Washington DC.
            This lead to situations where groups of immigrants that were assigned consecutive A numbers may have
            been in the same line at the same office on the same day.
          </Body>
          <Body>
            During this time period some families would all apply for visas at the same time, and have sequential A
            numbers assigned to them. Something you need to remember is that this was a time way before everything
            was digitized. Everything was on paper. Applications and forms would be filled out locally and sent to
            the INS for processing in Washington DC. Depending on the order that forms would be delivered and
            processed. If someone picked up a stack of forms that were from one location, they would all
            get A numbers allocated together at the same time.
          </Body>
          <Body>
            This process would sometimes be inconsistent. It was being performed by humans after all. A worker
            at the INS could easily get forms mixed up, or choose to process applications in a different
            order from one day to the next.
          </Body>

          <SubTitle>
            Hypothesis
          </SubTitle>
          <Body>
            The hypothesis is that we can use what we know about sequential A numbers and graph analysis to
            fill in gaps in publicly available data with some degree of certainty. Given the historical
            context this seems logical.
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
            records available, but only for people that are or would be at least 100 years of age. Much of
            the data that is available is still very incomplete. Some records may have a country of origin,
            but no port of entry for example.
          </Body>

          <div style={{display: 'flex', alignItems: 'center', marginTop: 20}}>
            <IconButton onClick={() => (
              downloadTextFile('filtered_data.json', filtered_data, 'application/json')
            )}>
              <GetAppIcon/>
            </IconButton>
            <Typography variant={'body2'}>
              Download Full Data
            </Typography>
          </div>
          <Paper className={classes.dataPaper}>
            <DataGrid
              columns={[
                {field: 'name', width: 140, headerName: 'Name'},
                {field: 'anum', width: 150, headerName: 'A Number'},
                {field: 'naturalization location', width: 180, headerName: 'Nat. Location'},
                {field: 'naturalization date', width: 180, type: 'date', headerName: 'Nat. Date'},
                {field: 'country', width: 200, headerName: 'Country of Origin'},
              ]}
              rows={filtered_data}
              pageSize={25}
              rowsPerPageOptions={[25, 50, 100]}
            />
          </Paper>

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
            is just the layout. It is deciding what becomes a node, and what becomes a connection. If we
            construct the graph in such a way, we can run common algorithms to find patterns in the data.
          </Body>
          <Body>
            The main form of analysis that could help fill in gaps in the data is something called community
            detection. The objective of community detection is to find groupings of nodes within the graph
            structure. This is how places like facebook can determine who are in groups on their platform.
          </Body>

          <SubTitle>
            First Attempt - Community Detection
          </SubTitle>
          <Body>
            The most naive approach to the problem is to create a graph with all A numbers connected to
            the next one in a long line, then connect the A number to their naturalization location.
            We could take this structure and run basic community detection algorithms to get groupings of
            people with close A numbers, and common locations.
          </Body>
          <Body>
            An example of this topology can be seen below. We have 5 A numbers in blue in a line. Each
            one is pointing to the next greatest A number in the data. Try hovering over a node to see
            its label.
          </Body>
          <Graph
            title={"Sequential Sample"}
            data={{
              nodes: [
                {id: 'New York', type: 'location'}, {id: 'San Francisco', type: 'location'},
                {id: 1, type: 'anum'}, {id: 2, type: 'anum'}, {id: 3, type: 'anum'},
                {id: 4, type: 'anum'}, {id: 5, type: 'anum'},
              ],
              links: [
                {source: 1, target: 2}, {source: 2, target: 3}, {source: 3, target: 4}, {source: 4, target: 5},
                {source: 1, target: 'New York'}, {source: 2, target: 'New York'}, {source: 3, target: 'New York'},
                {source: 4, target: 'San Francisco'}, {source: 5, target: 'San Francisco'},
              ],
            }}
          />
          <Body>
            When you run common community detection algorithms on this graph there are results, but unfortunately
            they do not need much. Just linking sequential nodes with huge gaps between them yields incomplete
            results.
          </Body>

          <SubTitle>
            Second Attempt - Branching & Linking
          </SubTitle>
          <Body>
            The second layout is significantly more effective. We link together A numbers same as before,
            but there is a catch. The connection is only created if the next A number is within 1000 of the
            last. Then same as before, the a numbers are linked to the naturalization location associated
            with them.
          </Body>
          <Body>
            The graph below shows all the people in the dataset that were naturalized in New York from
            1940-1945. New York is the center node, and the people are the nodes that radiate out from
            the center. Try hovering over a node to see its label.
          </Body>
          <Graph
            title={'New York Branch Graph'}
            data={new_york_graph_branch}
          />

          <Body>
            Taking the previous graph, linking together sequential A numbers then removing nodes that do
            not have a sequential A number in New York yields the graph below.
          </Body>
          <Graph
            title={'New York Branch & Link Graph'}
            data={new_york_graph_branch_link}
          />

          <Body>
            The previous graph is still a little crowded. It can be cleaned up by removing unnecessary
            connections. The next graph removes all links from the New York node to the A number nodes
            except for those at the beginning of the chain. This representation is the closest to
            proving the core hypothesis that I can get.
          </Body>
          <Body>
            There are a few chains here, but it is not enough to prove the hypothesis. Without a more
            complete dataset, there is not much more to show. The longest chain is only 4 A numbers long.
            These chains could simply be coincidence. If the hypothesis is correct, we would expect there to
            be many more, and much longer chains with a more complete dataset.
          </Body>
          <Graph
            title={'New York Branch, Link & Clean Graph'}
            data={new_york_graph_branch_link_clean}
            h={500}
          />

          <SubTitle>
            Conclusion
          </SubTitle>
          <Body>
            Unfortunately these experiments did not yield the results I was hoping. The main problem is
            the data itself. The whole theory rests upon the idea that we
            have sequential A numbers to analyze. The reality is that with the data available, there are
            huge gaps in the A number values. There may be thousands of A numbers between one and the next.
          </Body>
          <Body>
            The hypothesis makes sense in context but the proof I was able to find is incomplete and
            unconvincing. For this analysis to have worked, I would have needed a much more complete
            dataset. It is not so much a matter of the size of the dataset, but rather the A numbers
            within it. If I had even just a few stretches of sequential A numbers, I could start to
            fill in the unknowns.
          </Body>

          <SubTitle>
            Credits
          </SubTitle>
          <Body>
            Marian Smith provided historical context on how A numbers were allocated at USCIS.
            Professor Benjamin Schmidt from NYU provided context, and the data used to create
            these visualizations. Thank you to Marian Smith and Benjamin Schmidt.
          </Body>
        </Container>

        <footer className={classes.footer}>
          <Container maxWidth="sm">
            <div style={{display: 'flex', alignItems: 'center'}}>
              <IconButton
                size={'small'}
                className={classes.linkIcon}
                href={'https://github.com/wabscale/hist-ua-175-final'}
                target={"_blank"}
                rel={"noreferrer"}
              >
                <GitHubIcon/>
              </IconButton>
              <Typography variant="body1">
                Source is on GitHub
              </Typography>
            </div>
            <Typography variant="body2" color="textSecondary">
              {'Copyright © '}
              <Link color="inherit" href="https://github.com/wabscale">
                John Cunniff
              </Link>{' '}
              {new Date().getFullYear()}
              {'.'}
            </Typography>
          </Container>
        </footer>
      </ThemeProvider>
    </div>
  );
}

export default App;
