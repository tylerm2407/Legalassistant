import '@testing-library/jest-dom'
import { toHaveNoViolations } from 'jest-axe'

expect.extend(toHaveNoViolations)

// Mock scrollIntoView which doesn't exist in jsdom
Element.prototype.scrollIntoView = jest.fn();
