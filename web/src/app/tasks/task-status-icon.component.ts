import { Component, Input } from '@angular/core';

@Component({
  selector: 'task-status-icon',
  template: `
    <container-element [ngSwitch]="status">
      <nb-icon *ngSwitchCase="'pending'" icon="radio-button-off" status="basic" nbTooltip="Pending"></nb-icon>
      <nb-icon *ngSwitchCase="'in_progress'" icon="radio-button-on" status="info" nbTooltip="In Progress"></nb-icon>
      <nb-icon *ngSwitchCase="'succeeded'" icon="checkmark-circle-2" status="success" nbTooltip="Succeeded"></nb-icon>
      <nb-icon *ngSwitchCase="'failed'" icon="alert-circle" status="danger" nbTooltip="Failed"></nb-icon>
      <nb-icon *ngSwitchDefault icon="question-mark-circle"></nb-icon>
    </container-element>
  `,
})
export class TaskStatusIconComponent {
  @Input() status: String = 'pending'

  constructor() { }
}
