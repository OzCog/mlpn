#!/usr/bin/env node

const { execSync } = require('child_process');

// Configuration
const REPO_OWNER = 'OzCog';
const REPO_NAME = 'mlpn';
const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const PHASE = process.env.PHASE || 'all';
const DRY_RUN = process.env.DRY_RUN === 'true';

// Phase definitions based on the issue description
const phases = {
  1: {
    title: "Phase 1: Cognitive Primitives & Foundational Hypergraph Encoding",
    objective: "Establish the atomic vocabulary and bidirectional translation mechanisms between ko6ml primitives and AtomSpace hypergraph patterns.",
    subSteps: [
      {
        title: "Scheme Cognitive Grammar Microservices",
        description: "Design modular Scheme adapters for agentic grammar AtomSpace.\nImplement round-trip translation tests (no mocks).",
        labels: ["phase-1", "scheme", "microservices", "grammar"]
      },
      {
        title: "Tensor Fragment Architecture", 
        description: "Encode agent/state as hypergraph nodes/links with tensor shapes: `[modality, depth, context, salience, autonomy_index]`.\nDocument tensor signatures and prime factorization mapping.",
        labels: ["phase-1", "tensor", "hypergraph", "architecture"]
      },
      {
        title: "Phase 1 Verification",
        description: "Exhaustive test patterns for each primitive and transformation.\nVisualization: Hypergraph fragment flowcharts.",
        labels: ["phase-1", "verification", "testing", "visualization"]
      }
    ]
  },
  2: {
    title: "Phase 2: ECAN Attention Allocation & Resource Kernel Construction",
    objective: "Infuse the network with dynamic, ECAN-style economic attention allocation and activation spreading.",
    subSteps: [
      {
        title: "Kernel & Scheduler Design",
        description: "Architect ECAN-inspired resource allocators (Scheme + Python).\nIntegrate with AtomSpace for activation spreading.",
        labels: ["phase-2", "ecan", "kernel", "scheduler", "atomspace"]
      },
      {
        title: "Dynamic Mesh Integration",
        description: "Benchmark attention allocation across distributed agents.\nDocument mesh topology and dynamic state propagation.",
        labels: ["phase-2", "mesh", "distributed", "benchmarking"]
      },
      {
        title: "Phase 2 Verification",
        description: "Real-world task scheduling and attention flow tests.\nFlowchart: Recursive resource allocation pathways.",
        labels: ["phase-2", "verification", "testing", "flowchart"]
      }
    ]
  },
  3: {
    title: "Phase 3: Neural-Symbolic Synthesis via Custom ggml Kernels",
    objective: "Engineer custom ggml kernels for seamless neural-symbolic computation and inference.",
    subSteps: [
      {
        title: "Kernel Customization",
        description: "Implement symbolic tensor operations in ggml.\nDesign neural inference hooks for AtomSpace integration.",
        labels: ["phase-3", "ggml", "kernels", "neural-symbolic"]
      },
      {
        title: "Tensor Signature Benchmarking",
        description: "Validate tensor operations with real data (no mocks).\nDocument: Kernel API, tensor shapes, performance metrics.",
        labels: ["phase-3", "benchmarking", "validation", "documentation"]
      },
      {
        title: "Phase 3 Verification",
        description: "End-to-end neural-symbolic inference pipeline tests.\nFlowchart: Symbolic ↔ Neural pathway recursion.",
        labels: ["phase-3", "verification", "e2e-testing", "pipeline"]
      }
    ]
  },
  4: {
    title: "Phase 4: Distributed Cognitive Mesh API & Embodiment Layer",
    objective: "Expose the network via REST/WebSocket APIs; bind to Unity3D, ROS, and web agents for embodied cognition.",
    subSteps: [
      {
        title: "API & Endpoint Engineering",
        description: "Architect distributed state propagation, task orchestration APIs.\nEnsure real endpoints—test with live data, no simulation.",
        labels: ["phase-4", "api", "rest", "websocket", "distributed"]
      },
      {
        title: "Embodiment Bindings",
        description: "Implement Unity3D/ROS/WebSocket interfaces.\nVerify bi-directional data flow and real-time embodiment.",
        labels: ["phase-4", "unity3d", "ros", "embodiment", "bindings"]
      },
      {
        title: "Phase 4 Verification",
        description: "Full-stack integration tests (virtual & robotic agents).\nFlowchart: Embodiment interface recursion.",
        labels: ["phase-4", "verification", "integration", "robotics"]
      }
    ]
  },
  5: {
    title: "Phase 5: Recursive Meta-Cognition & Evolutionary Optimization",
    objective: "Enable the system to observe, analyze, and recursively improve itself using evolutionary algorithms.",
    subSteps: [
      {
        title: "Meta-Cognitive Pathways",
        description: "Implement feedback-driven self-analysis modules.\nIntegrate MOSES (or equivalent) for kernel evolution.",
        labels: ["phase-5", "meta-cognition", "feedback", "moses", "evolution"]
      },
      {
        title: "Adaptive Optimization",
        description: "Continuous benchmarking, self-tuning of kernels and agents.\nDocument: Evolutionary trajectories, fitness landscapes.",
        labels: ["phase-5", "optimization", "self-tuning", "evolutionary"]
      },
      {
        title: "Phase 5 Verification",
        description: "Run evolutionary cycles with live performance metrics.\nFlowchart: Meta-cognitive recursion.",
        labels: ["phase-5", "verification", "metrics", "recursion"]
      }
    ]
  },
  6: {
    title: "Phase 6: Rigorous Testing, Documentation, and Cognitive Unification",
    objective: "Achieve maximal rigor, transparency, and recursive documentation—approaching cognitive unity.",
    subSteps: [
      {
        title: "Deep Testing Protocols",
        description: "For every function, perform real implementation verification.\nPublish test output, coverage, and edge cases.",
        labels: ["phase-6", "testing", "verification", "coverage"]
      },
      {
        title: "Recursive Documentation",
        description: "Auto-generate architectural flowcharts for every module.\nMaintain living documentation: code, tensors, tests, evolution.",
        labels: ["phase-6", "documentation", "flowcharts", "architecture"]
      },
      {
        title: "Cognitive Unification",
        description: "Synthesize all modules into a unified tensor field.\nDocument emergent properties and meta-patterns.",
        labels: ["phase-6", "unification", "synthesis", "emergent-properties"]
      }
    ]
  }
};

// Function to create GitHub issue using gh CLI
function createIssue(title, body, labels) {
  const labelArgs = labels.map(label => `--label "${label}"`).join(' ');
  const command = `gh issue create --title "${title}" --body "${body}" ${labelArgs} --repo ${REPO_OWNER}/${REPO_NAME}`;
  
  if (DRY_RUN) {
    console.log(`[DRY RUN] Would create issue: ${title}`);
    console.log(`Labels: ${labels.join(', ')}`);
    console.log(`Body preview: ${body.substring(0, 100)}...`);
    console.log('---');
    return;
  }
  
  try {
    const result = execSync(command, { encoding: 'utf8' });
    console.log(`✅ Created issue: ${title}`);
    console.log(`   URL: ${result.trim()}`);
  } catch (error) {
    console.error(`❌ Failed to create issue: ${title}`);
    console.error(`   Error: ${error.message}`);
  }
}

// Function to generate issue body
function generateIssueBody(phase, subStep) {
  const flowchartSection = phase.title.includes('Phase 1') ? `

## Flowchart Reference
This phase contributes to the overall recursive implementation pathway:

\`\`\`
st=>start: Agentic Grammar Input
e1=>operation: Scheme Adapter Translation
e2=>operation: AtomSpace Hypergraph Encoding
e3=>operation: Tensor Shape Assignment
e4=>operation: ECAN Attention Kernel
e5=>operation: ggml Symbolic Kernel
e6=>operation: Distributed API Propagation
e7=>operation: Embodiment Interface Binding
e8=>operation: Meta-Cognitive Feedback
e9=>operation: Evolutionary Optimization
e10=>end: Unified Cognitive Tensor Field

st->e1->e2->e3->e4->e5->e6->e7->e8->e9->e10
\`\`\`
` : '';

  return `## Phase Objective
${phase.objective}

## Implementation Details
${subStep.description}

## Acceptance Criteria
- [ ] All implementation is completed with real data (no mocks or simulations)
- [ ] Comprehensive tests are written and passing
- [ ] Documentation is updated with architectural diagrams
- [ ] Code follows recursive modularity principles
- [ ] Integration tests validate the functionality

## Related to
This is part of the **${phase.title}** which aims to build a Distributed Agentic Cognitive Grammar Network.

${flowchartSection}

---
*This issue was automatically generated as part of the cognitive network development process.*`;
}

// Main function
function main() {
  console.log('🚀 Creating Cognitive Network Issues...');
  console.log(`Phase: ${PHASE}`);
  console.log(`Dry Run: ${DRY_RUN}`);
  console.log('');

  // Determine which phases to process
  const phasesToProcess = PHASE === 'all' ? Object.keys(phases) : [PHASE];
  
  if (!phasesToProcess.every(p => phases[p])) {
    console.error('❌ Invalid phase specified. Valid phases are: 1, 2, 3, 4, 5, 6, all');
    process.exit(1);
  }

  // Create milestone issue for each phase
  phasesToProcess.forEach(phaseNum => {
    const phase = phases[phaseNum];
    
    // Create main phase issue
    const phaseBody = `## Objective
${phase.objective}

## Sub-Steps
${phase.subSteps.map((step, index) => `${index + 1}. **${step.title}**`).join('\n')}

## Implementation Approach
This phase follows recursive modularity principles and requires:
- Real implementation verification (no mocks)
- Comprehensive testing protocols
- Architectural documentation with flowcharts
- Integration with the distributed cognitive mesh

## Progress Tracking
- [ ] Phase planning completed
- [ ] Sub-issues created and assigned
- [ ] Implementation in progress
- [ ] Testing and verification
- [ ] Documentation and integration
- [ ] Phase completion and handoff

---
*This is a milestone issue for tracking the overall progress of ${phase.title}.*`;

    createIssue(
      phase.title,
      phaseBody,
      [`phase-${phaseNum}`, 'milestone', 'cognitive-network']
    );

    // Create sub-step issues
    phase.subSteps.forEach(subStep => {
      const issueBody = generateIssueBody(phase, subStep);
      createIssue(
        `${phase.title}: ${subStep.title}`,
        issueBody,
        [...subStep.labels, 'cognitive-network']
      );
    });
  });

  console.log('');
  console.log('✨ Issue creation process completed!');
}

// Run the script
if (require.main === module) {
  main();
}