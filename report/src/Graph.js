import React from 'react';
import Paper from '@material-ui/core/Paper';
import Typography from '@material-ui/core/Typography';
import {makeStyles} from '@material-ui/core/styles';
import * as d3 from 'd3';

export const height = 250;
export const width = 500;


const drag = (simulation) => {
  function dragstarted(event) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    event.subject.fx = event.subject.x;
    event.subject.fy = event.subject.y;
  }

  function dragged(event) {
    event.subject.fx = event.x;
    event.subject.fy = event.y;
  }

  function dragended(event) {
    if (!event.active) simulation.alphaTarget(0);
    event.subject.fx = null;
    event.subject.fy = null;
  }

  return d3.drag()
    .on('start', dragstarted)
    .on('drag', dragged)
    .on('end', dragended);
};


const graphIt = (data, w, h) => (svg) => {
  const links = data.links.map(d => Object.create(d));
  const nodes = data.nodes.map(d => Object.create(d));

  svg._groups[0][0].innerHTML = '';

  const scale = d3.scaleOrdinal(d3.schemeCategory10);
  const color = (d) => scale(d.type);

  const simulation = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links).id(d => d.id))
    .force("center", d3.forceCenter(w / 2, h / 2))
    .force("charge", d3.forceManyBody().strength(-50))
    .force("x", d3.forceX())
    .force("y", d3.forceY())

  svg.append('svg:defs').append('svg:marker')
      .attr('id', 'triangle')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 15)
      .attr('refY', -0.5)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M 0,-5L10,0L0,5')
      .style('fill', '#aaa');

  const link = svg.append('g')
      .attr('stroke', '#aaa')
      .attr('stroke-opacity', 0.6)
      .selectAll('line')
      .data(links)
      .join('line')
      .attr('stroke-width', 1)
      .attr('marker-end', 'url(#triangle)');

  const node = svg.append('g')
      .attr('stroke', '#fff')
      .attr('stroke-width', 1.5)
      .selectAll('circle')
      .data(nodes)
      .join('circle')
      .attr('id', (d) => d.id)
      .attr('r', 5)
      .attr('class', 'graph-node')
      .attr('fill', color)
      .call(drag(simulation));

  // const link = svg.append("g")
  //   .attr("stroke", "#999")
  //   .attr("stroke-opacity", 0.6)
  //   .selectAll("line")
  //   .data(links)
  //   .join("line")
  //   .attr("stroke-width", d => Math.sqrt(d.value));
  //
  // const node = svg.append("g")
  //   .attr("stroke", "#fff")
  //   .attr("stroke-width", 1.5)
  //   .selectAll("circle")
  //   .data(nodes)
  //   .join("circle")
  //   .attr("r", 5)
  //   .attr("fill", color)
  //   .call(drag(simulation));

  node.append("title")
    .text(d => d.id);

  simulation.on("tick", () => {
    link
      .attr("x1", d => d.source.x)
      .attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x)
      .attr("y2", d => d.target.y);

    node
      .attr("cx", d => d.x)
      .attr("cy", d => d.y);
  });

  return svg.node()
}

function useD3(renderChartFn, rerenderDeps) {
  const ref = React.useRef();

  React.useEffect(() => {
    renderChartFn(d3.select(ref.current));
  }, rerenderDeps);

  return ref;
}


const useStyles = makeStyles((theme) => ({
  paper: {
    padding: theme.spacing(1),
    margin: theme.spacing(3, 5),
  },
  title: {
    margin: theme.spacing(1, 2),
  },
}));

export default function Graph({title = null, data, w = width, h = height}) {
  const classes = useStyles();
  const ref = useD3(graphIt(data, w, h), []);

  return (
    <Paper className={classes.paper}>
      {title && <Typography variant="h5" className={classes.title}>
        {title}
      </Typography>}
      <svg
        ref={ref}
        viewBox={[0, 0, w, h]}
      />
      <div style={{display: 'flex', justifyContent: 'flex-end'}}>
        <Typography variant={'body2'}>
          Try dragging nodes around. Hover over for labels.
        </Typography>
      </div>
    </Paper>
  );

}